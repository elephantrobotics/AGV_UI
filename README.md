# AGV_UI

## 软件运行

1. 仓库地址: `https://github.com/elephantrobotics/AGV_UI.git`
2. 分支管理:
   - `Raspberry Pi`版本的机器请克隆`Visualize_OP`分支
   - `Jetson Nano`版本的机器请克隆`Vis_JN`分支
   - 合并版本可以克隆`Vis_Merge`分支
3. 依赖安装: `pip install -r requirements.txt`
4. 运行软件: `python operations.py`

## 软件维护
### PyQT5 翻译家使用

1. 安装翻译家：`pip install pyqt5-tools`
2. 根据自己的安装路径配置系统环境
3. 打开翻译文件，进行翻译
   ```shell
   # 添加翻译文件
   pylupdate5 -noobsolete .\operations.py -ts .\translation\operations_lang.ts
   ```
4. 翻译完成之后点击`发布`即可完成翻译