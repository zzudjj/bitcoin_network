def get_coinbase_reward(block_height: int) -> float:
    """获取 coinbase 奖励"""
    reward = 50.0
    for _ in range(0, block_height // 100):
        reward = reward / 2
    return reward