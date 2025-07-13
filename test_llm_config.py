"""
LLM配置使用示例
"""

import asyncio
from src.config import llm_config
from src.services.llm_api import create_llm_client
from src.player.llm_player import LLMPlayer


async def test_llm_setup():
    """测试LLM配置"""
    
    # 验证配置
    if not llm_config.validate():
        print(f"配置验证失败！当前类型: {llm_config.client_type}")
        if llm_config.client_type == "openai" and not llm_config.openai_api_key:
            print("请设置 OPENAI_API_KEY 环境变量")
        elif llm_config.client_type == "claude" and not llm_config.anthropic_api_key:
            print("请设置 ANTHROPIC_API_KEY 环境变量")
        return
    
    print(f"使用LLM类型: {llm_config.client_type}")
    
    # 创建LLM客户端
    client = create_llm_client(
        llm_config.client_type,
        **llm_config.get_client_kwargs()
    )
    
    # 创建AI玩家
    player = LLMPlayer(player_id=1, llm_client=client, name="测试AI")
    
    # 测试简单的生成
    test_prompt = {
        "role": "Test",
        "my_info": {"player_id": 1},
        "possible_actions": ["PASS"]
    }
    
    try:
        response = await client.generate(test_prompt)
        print(f"LLM响应: {response}")
        print("✅ LLM配置成功！")
    except Exception as e:
        print(f"❌ LLM测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_llm_setup())