1. ui还是不够美观。请参考mac的ui。比如，设置里面的两个文件夹选择的蓝色区域会重合。
同时，蓝色区域的边框和字体间距太小。
还有，配色不是很好看，感觉很廉价。如果可以，请你找github开源的ui方案或者包。
2. 点击图片右侧并不会展示图片。因此其他功能无法测试。
不过，为了让你更好理解，我将详细介绍一下。

我希望的标注过程：
1. 在网页某个地方可以设置json字段，明设置json字典里面的每个关键liang的名字和类型。然后标注时，在哪里弹出每个字段的空，如果是string则是填空，如果是bool，则是选项框，只能选TRUE或FALSE.
然后一番操作下来，可以直接导出json。

哦对，考虑到这是个vlmprompt，请设置：
1. 可以设置提示词
2. outputjson时，自动添加提示词。

举个例子
我想配置成如下json

  {
    "images": [
      "FINALPART/@Customer@023851.jpeg"
    ],
    "messages": [
      {
        "content": "<image> \n你是一个工业打印标签检测专家。\n只关注标签区域（金属凹陷处区域），金属凹陷处外的缺陷不予考虑，请按照以下缺陷类型分类检测标签质量：\n1. 缺失元素（文字、二维码等关键元素丢失）或过多元素（如打印本不应该有的元素）\n2. 偏移问题（标签位置偏移、字符偏移）\n3. 物理缺陷（气泡、皱褶、划痕、污渍、墨点,标签多打印，标签断裂、打印颠倒）\n4. 打印质量（字迹模糊、字迹黯淡、字符打印不完整、二维码打印质量、二维码打印不完整、打印字符错误等）\n5. 整体布局（元素排版问题）\n\n返回格式如下（JSON可以换行，便于阅读）：\n{\n  \"overall_status\": \"PASS\" 或 \"FAIL\",\n  \"defect_categories\": [\n    {\n      \"number\": 1,\n      \"category\": \"缺失元素\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 2,\n      \"category\": \"偏移问题\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 3,\n      \"category\": \"物理缺陷\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 4,\n      \"category\": \"打印质量\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 5,\n      \"category\": \"整体布局\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    }\n  ],\n  \"confidence_score\": 0.95,\n  \"processing_info\": {\n    \"stage\": \"defect_classification\",\n    \"template_matched\": true,\n    \"categories_checked\": [\"缺失元素\", \"偏移问题\", \"物理缺陷\", \"打印质量\", \"整体布局\"]\n  }\n}\n\n请只返回这个JSON格式的内容，JSON可以换行以便阅读。",
        "role": "user"
      },
      {
        "content": "{\n  \"overall_status\": \"FAIL\",\n  \"defect_categories\": [\n    {\n      \"number\": 1,\n      \"category\": \"缺失元素\",\n      \"compliance\": true,\n      \"result\": \"所有关键元素完整存在\",\n      \"details\": []\n    },\n    {\n      \"number\": 2,\n      \"category\": \"偏移问题\",\n      \"compliance\": false,\n      \"result\": \"标签偏移至右上角，超出金属凹陷处与外部的交界线。\",\n      \"details\": []\n    },\n    {\n      \"number\": 3,\n      \"category\": \"物理缺陷\",\n      \"compliance\": false,\n      \"result\": \"标签右下角有褶皱。\",\n      \"details\": []\n    },\n    {\n      \"number\": 4,\n      \"category\": \"打印质量\",\n      \"compliance\": false,\n      \"result\": \"第二行应为F01R，其中0打印出现缺口\",\n      \"details\": []\n    },\n    {\n      \"number\": 5,\n      \"category\": \"整体布局\",\n      \"compliance\": true,\n      \"result\": \"整体布局规整\",\n      \"details\": []\n    }\n  ],\n  \"confidence_score\": 0.95,\n  \"processing_info\": {\n    \"stage\": \"defect_classification\",\n    \"template_matched\": true,\n    \"categories_checked\": [\n      \"缺失元素\",\n      \"偏移问题\",\n      \"物理缺陷\",\n      \"打印质量\",\n      \"整体布局\"\n    ]\n  }\n}",
        "role": "assistant"
      }
    ]
  },

  总结一下这个json的需求：

  1. 包含路径。
  2. 提示词自动注入。
  3. 每个字段，如，overall_status，自动写入json。

  goooooood luck。感谢ai。