# -*- coding: utf-8 -*-
# @Time    : 2019/8/26 9:12
# @Author  : Tony
"""神经网络测试用例"""
import numpy as np
from datetime import datetime

from app.cta_strategy.neural_network import NeuralNetwork
from trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager

if __name__ == '__main__':

    input_data_len = 100  # 输入60根分钟K线的数据（高开低收量）= 300数据点
    target_data_len = 15  # 预测10分钟后的高点
    profit_percent = 0.005  # 1万20 盈利点 - 1万1.5 * 2 手续费 = 17 元 单笔

    input_nodes = input_data_len * 5
    hidden_nodes = input_data_len * 3
    output_nodes = 3
    learning_rate = 0.1

    symbol = 'rb1910'
    exchange = Exchange.SHFE
    interval = Interval.MINUTE
    start = datetime(2019, 8, 10)
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
        for train_index in range(train_data_len - input_data_len - target_data_len + 1):
            input_bar_data = bar_data[train_index:train_index + input_data_len]
            target_bar_data = bar_data[train_index + input_data_len:train_index + input_data_len + target_data_len]

            input_max_high = max([x.high_price for x in input_bar_data])
            input_max_volume = max([x.volume for x in input_bar_data])
            input_data = np.array([[x.high_price / input_max_high, x.open_price / input_max_high
                                       , x.low_price / input_max_high, x.close_price / input_max_high
                                       , x.volume / input_max_volume]
                                   for x in input_bar_data]).reshape(1, input_nodes)

            input_last_close = input_bar_data[-1].close_price
            target_max_high = max([x.high_price for x in target_bar_data])
            target_profit_percent = (target_max_high - input_last_close) / input_last_close

            target_data = np.zeros(output_nodes) + 0.01
            if target_profit_percent > profit_percent:  # 多开信号
                target_data[1] = 0.99
            elif target_profit_percent < -profit_percent:  # 空开信号
                target_data[2] = 0.99
            else:
                target_data[0] = 0.99

            neuralNetwork.train(input_data, target_data)
            pass

    print(f"Start test range: {test_data_len - input_data_len - target_data_len + 1}, date: {bar_data[train_data_len].datetime}")
    scordcard = []
    prediction_result = []
    actual_result = []
    for test_index in range(test_data_len - input_data_len - target_data_len + 1):
        input_bar_data = bar_data[train_data_len + test_index: train_data_len + test_index + input_data_len]
        target_bar_data = bar_data[train_data_len + test_index + input_data_len
                                   : train_data_len + test_index + input_data_len + target_data_len]

        input_max_high = max([x.high_price for x in input_bar_data])
        input_max_volume = max([x.volume for x in input_bar_data])
        input_data = np.array([[x.high_price / input_max_high, x.open_price / input_max_high
                                   , x.low_price / input_max_high, x.close_price / input_max_high
                                   , x.volume / input_max_volume]
                               for x in input_bar_data]).reshape(1, input_nodes)

        input_last_close = input_bar_data[-1].close_price
        target_max_high = max([x.high_price for x in target_bar_data])
        target_profit_percent = (target_max_high - input_last_close) / input_last_close

        output = neuralNetwork.query(input_data)
        output_label = int(np.argmax(output))

        current_label = 0
        if target_profit_percent > profit_percent:  # 多开信号
            current_label = 1
            print(bar_data[train_data_len + test_index + input_data_len].datetime, input_last_close, target_max_high, target_profit_percent)
        elif target_profit_percent < -profit_percent:  # 空开信号
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
