"""
MinerU 自动化安装和模型下载脚本
功能：
1. 升级 pip
2. 安装 uv 包管理器
3. 安装项目依赖 (requirements.txt)
4. 安装 mineru[core]
5. 自动下载 pipeline 模型（使用 modelscope 源）
"""
import subprocess
import sys
import os
from pathlib import Path

# 使用阿里云镜像源
PYPI_MIRROR = "https://mirrors.aliyun.com/pypi/simple"

def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"执行命令: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        print(result.stdout)
        print(f"✅ {description} 完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败！")
        print(f"错误信息: {e.stderr}")
        return False

def check_requirements_file():
    """检查 requirements.txt 是否存在"""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("⚠️ 未找到 requirements.txt 文件")
        return False
    return True

def download_models():
    """自动下载模型（非交互式）"""
    print(f"\n{'='*60}")
    print(f"📥 开始下载 MinerU 模型")
    print(f"{'='*60}")
    
    # 检查模型是否已存在
    mineru_config = Path.home() / "mineru.json"
    if mineru_config.exists():
        print(f"✅ 检测到配置文件: {mineru_config}")
        print("模型可能已经下载，如需更新请手动运行: mineru-models-download")
        
        choice = input("是否重新下载模型？(y/n) [n]: ").lower()
        if choice != 'y':
            print("跳过模型下载")
            return True
    
    # 尝试方法1: 创建临时文件自动输入
    print("方法1: 使用临时文件自动输入...")
    env = os.environ.copy()
    env['MINERU_MODEL_SOURCE'] = 'modelscope'
    
    try:
        # 创建临时输入文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('modelscope\n')
            f.write('pipeline\n')
            temp_file = f.name
        
        # Windows 和 Linux/Mac 使用不同的重定向方式
        if sys.platform == 'win32':
            cmd = f'mineru-models-download < "{temp_file}"'
        else:
            cmd = f'mineru-models-download < {temp_file}'
        
        print(f"执行命令: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 删除临时文件
        try:
            os.unlink(temp_file)
        except:
            pass
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0 or "successfully" in result.stdout.lower():
            print(f"✅ 模型下载完成！")
            
            # 显示模型路径
            if mineru_config.exists():
                print(f"\n模型配置已写入: {mineru_config}")
                try:
                    import json
                    with open(mineru_config, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if 'models-dir' in config:
                            print(f"模型路径: {config['models-dir']}")
                except:
                    pass
            
            return True
        else:
            print(f"⚠️ 自动下载失败")
            raise Exception("自动下载失败")
            
    except Exception as e:
        print(f"⚠️ 自动下载方式失败: {e}")
        
        # 方法2: 回退到交互式下载
        print("\n" + "="*60)
        print("方法2: 启动交互式下载")
        print("="*60)
        print("\n请按以下步骤操作：")
        print("1. 在提示 'Please select the model download source' 时输入: modelscope")
        print("2. 在提示 'Please select the model type to download' 时输入: pipeline")
        print("\n按回车键继续...")
        input()
        
        result = subprocess.run(
            "mineru-models-download",
            shell=True,
            env=env
        )
        
        if result.returncode == 0:
            print(f"\n✅ 模型下载完成！")
            print(f"配置文件位置: {Path.home() / 'mineru.json'}")
            return True
        else:
            print(f"❌ 模型下载失败")
            return False

def main():
    """主函数"""
    print(f"""
    {'='*60}
    MinerU 自动化安装脚本
    {'='*60}
    本脚本将执行以下步骤：
    1. 升级 pip 到最新版本
    2. 安装 uv 包管理器
    3. 安装项目依赖 (requirements.txt)
    4. 安装 mineru[core] 核心包
    5. 下载 pipeline 模型（使用 modelscope 源）
    
    使用镜像源: {PYPI_MIRROR}
    
    注意事项：
    - 模型会自动下载到系统默认位置
    - 模型路径会写入到用户目录下的 mineru.json
    - 如需移动模型，请手动修改 mineru.json 中的路径
    {'='*60}
    """)
    
    input("按回车键开始安装...")
    
    # 步骤1: 升级 pip
    if not run_command(
        f'pip install --upgrade pip -i {PYPI_MIRROR}',
        "升级 pip"
    ):
        print("⚠️ pip 升级失败，是否继续？")
        if input("输入 y 继续，其他键退出: ").lower() != 'y':
            return
    
    # 步骤2: 安装 uv
    if not run_command(
        f'pip install uv -i {PYPI_MIRROR}',
        "安装 uv 包管理器"
    ):
        print("⚠️ uv 安装失败，是否继续？")
        if input("输入 y 继续，其他键退出: ").lower() != 'y':
            return
    
    # 步骤3: 安装项目依赖
    if check_requirements_file():
        if not run_command(
            f'uv pip install -r requirements.txt -i {PYPI_MIRROR}',
            "安装项目依赖 (requirements.txt)"
        ):
            print("⚠️ 项目依赖安装失败，是否继续？")
            if input("输入 y 继续，其他键退出: ").lower() != 'y':
                return
    else:
        print("⚠️ 跳过项目依赖安装")
    
    # 步骤4: 安装 mineru
    if not run_command(
        f'uv pip install -U "mineru[core]" -i {PYPI_MIRROR}',
        "安装 mineru[core]"
    ):
        print("❌ mineru 安装失败！")
        return
    
    # 步骤5: 下载模型
    if not download_models():
        print("⚠️ 模型下载失败或被跳过")
        print("\n你可以稍后手动运行以下命令下载模型：")
        print("mineru-models-download")
        print("\n按照提示选择:")
        print("  - 下载源: modelscope")
        print("  - 模型类型: pipeline")
    
    # 完成提示
    mineru_config = Path.home() / "mineru.json"
    model_info = ""
    if mineru_config.exists():
        try:
            import json
            with open(mineru_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'models-dir' in config:
                    model_info = f"\n    模型路径: {config['models-dir']}"
        except:
            pass
    
    print(f"""
    {'='*60}
    ✅ 安装完成！
    {'='*60}
    
    配置文件位置: {mineru_config}{model_info}
    
    现在你可以使用 MinerU 了！
    
    测试命令:
    cd MinerU
    python test_parse.py
    
    如需移动模型文件:
    1. 移动模型文件夹到新位置
    2. 编辑 {mineru_config}
    3. 更新 "models-dir" 字段为新路径
    
    更新模型:
    mineru-models-download
    (注意：更新会下载到默认位置)
    {'='*60}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 安装过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)