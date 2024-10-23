
# 使用方法
1. environment.yml里是conda环境，使用下方命令安装。
```
conda env create -f environment.yml
```
2. 需要安装modelsim(推荐)或者iverilog并配置到环境变量
3. 进入conda，切换到当前目录，运行如下命令，参见cocotb文档。
```bash
make SIM=modelsim
```
或
```bash
make SIM=iverilog
```