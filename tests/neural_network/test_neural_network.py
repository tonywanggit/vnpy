# -*- coding: utf-8 -*-
# @Time    : 2019/8/26 9:12
# @Author  : Tony
"""神经网络测试用例"""
import numpy as np
from datetime import datetime

from app.cta_strategy.neural_network import NeuralNetwork
from trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager


def make_input_data(raw_data):
    input_max_high = max([x.high_price for x in raw_data])
    input_min_low = min([x.low_price for x in raw_data])
    input_price_range = input_max_high - input_min_low
    input_max_volume = max([x.volume for x in raw_data])

    def parse_price(price):
        return ((price - input_min_low) / input_price_range) + 0.001

    return np.array([[parse_price(x.high_price), parse_price(x.open_price), parse_price(x.low_price)
                         , parse_price(x.close_price), x.volume / input_max_volume] for x in raw_data])


def make_target_data(raw_data, last_close):
    max_high = max([x.high_price for x in raw_data])
    target_percent = (max_high - last_close) / last_close

    target_data_label = np.zeros(output_nodes) + 0.01
    if target_percent > long_profit_percent:  # 多开信号
        target_data_label[1] = 0.99
    elif target_percent < - short_profit_percent:  # 空开信号
        target_data_label[2] = 0.99
    else:
        target_data_label[0] = 0.99

    return target_data_label, target_percent, max_high


if __name__ == '__main__':
    input_data_len = 100  # 输入X根分钟K线的数据（高开低收量）= x * 5 个数据点
    target_data_len = 15  # 预测10分钟后的高点
    long_profit_percent = 0.002  # 1万20 盈利点 - 1万1.5 * 2 手续费 = 17 元 单笔
    short_profit_percent = 0.002  # 1万20 盈利点 - 1万1.5 * 2 手续费 = 17 元 单笔

    input_nodes = input_data_len * 5
    hidden_nodes = input_data_len * 7
    output_nodes = 3
    learning_rate = 0.1

    symbol = 'rb1910'
    exchange = Exchange.SHFE
    interval = Interval.MINUTE
    start = datetime(2019, 6, 10)
    end = datetime.now()

    neuralNetwork = NeuralNetwork(input_nodes, hidden_nodes, output_nodes, learning_rate)
    print("run nerual network")

    bar_data = database_manager.load_bar_data(symbol, exchange, interval, start, end)
    bar_data_len = len(bar_data)
    print(f"load bar data size {bar_data_len}, {interval}")

    if bar_data_len < 1000:
        print("need more data >= 50000")

    test_data_len = 200  # 测试集
    train_data_len = bar_data_len - test_data_len  # 训练集
    print(f"train data size: {train_data_len}, test data size: {test_data_len}")

    epochs = 1
    for e in range(epochs):
        print("Start epoch: ", e)
        train_range = train_data_len - input_data_len - target_data_len + 1
        for train_index in range(train_range):
            input_bar_data = bar_data[train_index:train_index + input_data_len]
            target_bar_data = bar_data[train_index + input_data_len:train_index + input_data_len + target_data_len]

            input_data = make_input_data(input_bar_data).reshape(1, input_nodes)
            target_data, _, _ = make_target_data(target_bar_data, input_bar_data[-1].close_price)

            neuralNetwork.train(input_data, target_data)
            pass

    test_range = test_data_len - input_data_len - target_data_len + 1
    print(f"Start test range: {test_range}, date: {bar_data[train_data_len].datetime}")

    scordcard = []
    prediction_result = []
    actual_result = []
    for test_index in range(test_range):
        test_target_index = train_data_len + test_index + input_data_len

        input_bar_data = bar_data[train_data_len + test_index: test_target_index]
        target_bar_data = bar_data[test_target_index: test_target_index + target_data_len]

        input_data = make_input_data(input_bar_data).reshape(1, input_nodes)
        input_last_close = input_bar_data[-1].close_price
        target_data, target_profit_percent, target_max_high = make_target_data(target_bar_data, input_last_close)

        output = neuralNetwork.query(input_data)
        output_label = int(np.argmax(output))

        current_label = 0
        if target_profit_percent > long_profit_percent:  # 多开信号
            current_label = 1
            print(bar_data[test_target_index].datetime, input_last_close, target_max_high, target_profit_percent)
        elif target_profit_percent < - short_profit_percent:  # 空开信号
            current_label = 2
        else:
            current_label = 0

        prediction_result.append(output_label)
        actual_result.append(current_label)

        if current_label == output_label:
            scordcard.append(1)
        else:
            scordcard.append(0)

    scordcard_array = np.asarray(scordcard)
    print("Performance = ", scordcard_array.sum() / scordcard_array.size)
    print(f"Predict Long {prediction_result.count(1)} , Short {prediction_result.count(2)}, Sleep {prediction_result.count(0)}")
    print(f"Actual Long {actual_result.count(1)} , Short {actual_result.count(2)}, Sleep {actual_result.count(0)}")
