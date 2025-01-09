def adjust_difficulty(previous_difficulty, actual_time, target_time=600, adjustment_interval=2016, max_adjustment_factor=4):
    """调整挖矿难度。"""
    # 计算难度调整比例
    adjustment_factor = actual_time / (target_time * adjustment_interval)
    # 限制调整幅度
    adjustment_factor = max(1 / max_adjustment_factor, min(adjustment_factor, max_adjustment_factor))
    # 计算新难度
    new_difficulty = previous_difficulty * adjustment_factor
    return new_difficulty
