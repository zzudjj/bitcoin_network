from node import Network, create_and_start_node
from cli import BitcoinCmd
DIR_BASE = 'data/'

network = Network()
create_and_start_node(node_id=0, network=network, dir=DIR_BASE+'djj')
create_and_start_node(node_id=1, network=network, dir=DIR_BASE+'zsy')
create_and_start_node(node_id=2, network=network, dir=DIR_BASE+'cby')
create_and_start_node(node_id=3, network=network, dir=DIR_BASE+'chr')
cmd = BitcoinCmd(network)
cmd.cmdloop()