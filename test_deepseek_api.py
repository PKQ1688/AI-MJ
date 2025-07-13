#!/usr/bin/env python3
"""
测试DeepSeek API连接的简单脚本
"""

import asyncio
from openai import AsyncOpenAI

async def test_deepseek_api():
    """测试DeepSeek API是否可用"""
    
    # 请在这里输入您的有效DeepSeek API Key
    api_key = input("请输入您的DeepSeek API Key: ").strip()
    
    if not api_key:
        print("❌ 未提供API Key")
        return False
    
    try:
        # 创建客户端
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        print("🔄 正在测试DeepSeek API连接...")
        
        # 发送测试请求
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello, please respond with 'API test successful'"},
            ],
            stream=False,
            max_tokens=50
        )
        
        content = response.choices[0].message.content.strip()
        print(f"✅ API测试成功！")
        print(f"📝 响应内容: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_deepseek_api())
    if success:
        print("\n🎉 DeepSeek API配置正确，可以用于麻将游戏！")
    else:
        print("\n⚠️  请检查API Key是否有效，或者网络连接是否正常。")
