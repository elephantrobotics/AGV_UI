# AGV_UI

## 运行软件

1. 克隆github 仓库地址：` https://github.com/elephantrobotics/AiKit_3D_UI.git`
2. 确保当前为**Visualize_OP**分支
3. 使用python运行该文件：
`
python operations.py  
`


### PyQT5 翻译家使用

1. 安装翻译家：`pip install pyqt5-tools`
2. 根据自己的安装路径配置系统环境
3. 打开翻译文件，进行翻译
    ```shell
        pylupdate5 -noobsolete .\operations.py -ts .\translation\operations_lang.ts
    ``` 
4. 翻译完成之后点击`发布`即可完成翻译