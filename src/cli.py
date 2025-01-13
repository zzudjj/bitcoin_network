import argparse
import cmd
from node import Network, create_and_start_node
from transaction import deserialize_transaction

DIR_BASE = 'data/'

class BitcoinCmd(cmd.Cmd):
    intro = '欢迎使用比特币网络命令行界面。输入 help查看命令列表。'
    prompt = '>>> '

    def __init__(self, network):
        super().__init__()
        self.network: Network = network

    def do_get_balance(self, arg):
        '获取余额: get_balance -dir <目录地址> -address <地址>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        parser.add_argument('-address', type=str, required=True, help='地址')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="getbalance", data=args.address)
        self.wait_reply()

    def do_create_tx(self, arg):
        '创建交易: create_tx -dir <目录地址> -to <地址1> <地址2> ... -value <金额1> <金额2> ... -tx_fee <交易费用>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        parser.add_argument('-to', nargs='+', required=True, help='接收地址')
        parser.add_argument('-value', nargs='+', type=float, required=True, help='交易金额')
        parser.add_argument('-tx_fee', type=float, default=0.05, help='交易费用')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        data = {'to': args.to, 'value': args.value, 'tx_fee': args.tx_fee}
        self.network.send_data(to_node_id=node_id, message_type="create_tx", data=data)
        self.wait_reply()

    def do_create_block(self, arg):
        '创建区块: create_block -dir <目录地址>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="create_block", data="")
        self.wait_reply()

    def do_get_best_height(self, arg):
        '获取最新区块高度: get_best_height -dir <目录地址>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="get_best_height", data="")
        self.wait_reply()

    def do_get_best_block_hash(self, arg):
        '获取最新区块哈希值: get_best_block_hash -dir <目录地址>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="get_best_block_hash", data="")
        self.wait_reply()

    def do_list_address(self, arg):
        '列出地址: list_address -dir <目录地址>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="list_address", data="")
        self.wait_reply()

    def do_print_blocks(self, arg):
        '打印区块链: print_blocks -dir <目录地址>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="print_blocks", data="")
        self.wait_reply()

    def do_get_tx(self, arg):
        '获取交易: get_tx -dir <目录地址> -tx_id <交易ID>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        parser.add_argument('-tx_id', type=str, required=True, help='交易ID')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="get_tx", data=args.tx_id)
        self.wait_reply()
    
    def do_get_block(self, arg):
        '获取区块: get_block -dir <目录地址> -block_hash <区块哈希>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        parser.add_argument('-block_hash', type=str, required=True, help='区块哈希')
        args = parser.parse_args(arg.split())
        node_id = self.network.mp.get(args.dir)
        if node_id is None:
            print(f"未找到目录为 {args.dir} 的节点")
            return
        self.network.send_data(to_node_id=node_id, message_type="get_block", data=args.block_hash)
        self.wait_reply()

    def do_start_node(self, arg):
        '运行节点: start_node -dir <目录地址>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-dir', type=str, required=True, help='节点目录')
        args = parser.parse_args(arg.split())
        node_id = max(self.network.mp.values()) + 1
        create_and_start_node(node_id=node_id, dir=args.dir, network=self.network)
        print(f"成功运行节点 {args.dir}，node_id为 {node_id}")

    def do_get_tx_id(self, arg):
        '获取交易ID: get_tx_id -data <交易序列化数据>'
        parser = argparse.ArgumentParser()
        parser.add_argument('-data', type=str, required=True, help='交易序列化数据')
        args = parser.parse_args(arg.split())
        tx = deserialize_transaction(bytes.fromhex(args.data))
        print(f"交易ID: {tx.hash()}")
    

    def do_exit(self, arg):
        '退出命令行界面: exit'
        print('退出命令行界面')
        return True

    def do_help(self, arg):
        '查看命令列表: help'
        print('命令列表:')
        print('  get_balance -dir <目录地址> -address <地址>  获取余额')
        print('  create_tx -dir <目录地址> -to <地址1> <地址2> ... -value <金额1> <金额2> ... -tx_fee <交易费用>  创建交易')
        print('  create_block -dir <目录地址>  创建区块')
        print('  get_best_height -dir <目录地址>  获取最新区块高度')
        print('  get_best_block_hash -dir <目录地址>  获取最新区块哈希值')
        print('  list_address -dir <目录地址>  列出地址')
        print('  print_blocks -dir <目录地址>  打印区块链')
        print('  get_tx -dir <目录地址> -tx_id <交易ID>  获取交易')
        print('  get_block -dir <目录地址> -block_hash <区块哈希>  获取区块')
        print('  start_node -dir <目录地址>  运行节点(如目录不存在程序会自动创建)')
        print('  get_tx_id -data <交易序列化数据>  获取交易ID')
        print('  exit  退出命令行界面')
    
    def wait_reply(self):
        while True:
            messages = self.network.get_messages(node_id=443)
            if len(messages) == 0:
                continue
            sender_id, message_type, data = messages[0]
            if message_type == "reply" and data == True:
                break
