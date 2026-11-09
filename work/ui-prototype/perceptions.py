"""Manually coded themes for the reviewed 30-day App Store snapshot."""
from datetime import datetime,timedelta
THEMES=[
('continuity','跨设备衔接不顺畅','问题','手机与电脑连接、状态同步或任务接续受阻。','1f067d884b6df42a0741d405 21085e1c30c417e2fa1b25fd 32651c4249c8beed675d4056 496fbc44967e4719c836490b 514cfa1587e017e1fac78095 5a592d9ee5777bb2b7836dbe 6597b7f38b33be88b60958dc 8349c530a898bdc188b7df24 8d5c002ebec7e83fe4d07c70 a677261ee3ccacd1aba9071d a978a05e1ed1cb5bfa87ae4d d42232baad56fa7fd569784e d7fe616b78b410cf6a90ba63 f5c7447940ecec32463ce8be'),
('slow','响应慢或执行卡顿','问题','等待回复、界面卡住、拥堵或任务执行停滞。','090af1dc713d1cbc2ff676ef 19cea335d5f5420f336f7e97 f408cffb7ac8e4f552a95b99 21085e1c30c417e2fa1b25fd 2186a4b6b18ff955883a9464 5c5d1c320e0f5dd4a2e6f3aa 786262594c129846631135c2 85c9cca921564ff04f8edf99 c2be4fce7d8f9b730fde68de d7fe616b78b410cf6a90ba63 e45120b09b1810fd99402a9e f3d3fb3cd9f413f3defd6ef8 d049778c5e9406cc0132efc9'),
('credits','额度与费用体验有阻碍','问题 / 诉求','积分消耗显示、领取方式、收费或额度限制影响使用。','46b8a98ae44fc2bbe8fbf590 4e9ec137cc0015c11af67fc3 5a592d9ee5777bb2b7836dbe 6c6a92e14e134a0babf84f72 786262594c129846631135c2 8a9a6736db48dc234ae46f3e 9dc2327a1e4a229995a1f6c8 fafcacbc411b9bc75755033c fc2f5f893928962dc2a586fe 3d9af75ae6ff5aa16f3f7065 98ba2c33b13535fabdcb30b2'),
('work','能帮助完成工作或创作','认可','完成工作问题、应用制作、代码、写作或内容创作。','7b45b5fc87ce9d1316e059ae ab3038bfdd70201007a9cc67 5d41bb178488ee932677a05a 8d5c002ebec7e83fe4d07c70 a83548e788834c12f18a2f15 a978a05e1ed1cb5bfa87ae4d 0ce1465439291e139ced0c43 467cbbf8c9d208e48a7a274b d6d6f68d7d838f48b04c986d d79f0061a9e1404bf97eb2ae'),
('accuracy','回答出错或没有理解要求','问题','评论明确涉及答题、计算、翻译、理解或执行要求的问题；没有独立测算准确率。','00ea4ac7f0e0cfe8721914de 66c7a761ca27575bc2289d64 8d5c002ebec7e83fe4d07c70 c2be4fce7d8f9b730fde68de e11981bad6b701725afb2136 91cfbe6ddf7bcde0c85e5040 b86b16dbec744e5a2e7e5606 c07501b152aaf4ee5c7a441f cbaf6eba7c57d3bd9b99f574 fd1c0348bc372340dd829c44 3c10907cab1d099f7124b4c4 54f8c8044b87f40b04c1b0e0'),
('conversation','任务中补充消息或延续上下文不便','问题 / 诉求','执行中追加要求、切换会话或上下文延续存在阻碍。','090af1dc713d1cbc2ff676ef e538a9dd3b6d5c951df02964 2186a4b6b18ff955883a9464 8d5c002ebec7e83fe4d07c70 ea1b03bec19d6c8d24a078d2'),
('login','登录或账号状态有问题','问题','登录失败、验证码收不到或账号掉线。','1f067d884b6df42a0741d405 4bf11aca3ff9cbbe7c4cddc3 a61ed5f23fe14dc29ff99db4'),
('update','更新体验有困扰','问题','无法更新、更新频繁或升级后体验变化；并非已确认的产品回归。','ab3038bfdd70201007a9cc67 5c5d1c320e0f5dd4a2e6f3aa 6f95393932414f6e34991e9c'),
('files','文件与知识库操作不够顺手','问题 / 诉求','文件上传、传输、分类、命名或批量处理有阻碍。','5048fc2f904c54ef4499ee49 5a592d9ee5777bb2b7836dbe eab3f2fc16b85d6df1e7a1e4 3942f4436be58d1f6a27ffcc 6f3c61f69b748b9b6defee62 7a7a326974723c9423ce5536 d0311d593045bcd61f536e32 f3449e07fe536d2c960c4002'),
('annotations','希望加强阅读批注与笔记','诉求','在 PDF 上标注、手写，并希望问答能理解标注。','3598ce446437b6e46d1e2aaa 529997f2b4f732fd6b0724e1'),
('research','整理资料与学习有帮助','认可','辅助备课、阅读、资料检索与分析、学习或梳理已有计划。','00bca34bcb20400ea69e15a3 270241e664bc0e20afa17ab3 348b8b9dd85a2dfb78b6f2f2 437a0dc17030a0cfb2b3187a 529997f2b4f732fd6b0724e1 5b777a413964a67b7f76808e 971f718ba31f29506be90c2f c3276facf4dae5818ea3d57b d6dbfbbd3da6e65ea1e6d1ea'),
('fast','响应快、使用顺畅','认可','评论明确提及速度快或操作顺手。','01644c42243084f4d2c8a2c9 971f718ba31f29506be90c2f c3276facf4dae5818ea3d57b d6dbfbbd3da6e65ea1e6d1ea dca9da5af51efd6109918980 df57f456f6f03bd84622874f'),
('understanding','沟通贴合、理解表达','认可','评论明确认可对意图和表达的理解。','9509f9508cfe0ed0eba236fa b55c2dbfd11271e50c67e000 d2dca551a5b2ee4d20f4d64b bb381c82b17837ace7156e42'),
('media-good','多媒体生成能力有吸引力','认可','评论提及生图、播客、海报、转文字、声音等功能的价值。','729feca73727a0dac7aeeaed b55c2dbfd11271e50c67e000 b754fa8248d98f8006b28583 680d2dcd05d9d50ff0613ecb ed4c32d9701e935b8bb4f944'),
('media-bad','图片或视频生成不够准确','问题','评论指出图像、视频生成效果或反复修改问题。','ed4c32d9701e935b8bb4f944 89eb09c2ef5780bdb6a80681'),
('companionship','有陪伴感、能安慰和理解人','认可','评论描述情绪回应、交流舒适、朋友感或陪伴；不评价长期效果。','023b86ee6f14c589ee35d9a9 08d8a001de97e063523e0871 2177d4643556bd0a4639f3d7 247b78cf48a3f45db80ce6db 34e6b582bfe0abd31521ae8f 355bbf536568ba2a1c3756b4 42d9c657cfc48293ab6ebec2 b9bdd6c3ad87148c3666c3b8 bec0083d12e824249e657b89 c07501b152aaf4ee5c7a441f e42b03f6c96cf0ccf3f2d7e8 fb0883e5e5d7ff12970463c4 6e73a6f8c76cd299f0d723d0 6fab83b34804c52f6d993b16 d7edd50a8e744205703efd80'),
('answers','日常答疑和解决问题有帮助','认可','认可咨询、建议或解决具体生活问题的价值。','42d9c657cfc48293ab6ebec2 8ab43e34d030204d115c4dae 16f54e932a68c41fa7d4adc6 19fa87aac56827930658e08a 28a4ffe13d76032f70d89c13 811f64bc32ede9c570d40257 d7edd50a8e744205703efd80 df57f456f6f03bd84622874f e4d63a655a1d6624ccba48ac'),
('agents','希望保留或恢复智能体入口','诉求','用户表达对智能体入口的依赖，不据此断言功能下线。','2cba01dbecbc943c4579cfde c63bdec220f478b8800f5797'),
('collaboration','希望增加任务、协作与角色能力','诉求','待办、日历、多人编辑和权限诉求。','76f4e7d47c1de9a5d8859fcb'),
('onboarding','希望有更清楚的使用引导','诉求','评论提出面向老年用户的教程与参与引导。','8a9a6736db48dc234ae46f3e'),
('prompts','希望支持提示词优化','诉求','手机端提示词优化功能请求。','e4ca23a2ffe61d67a26b590c'),
('models','模型选择与重连有诉求','问题 / 诉求','模型可用性或自定义模型重连相关反馈。','0bd7fad1d3d0441bac4c8f1a e16c56cbcfd12b7420e9f837')
]
def make_perceptions(data):
 end=datetime.fromisoformat(data['generated_at']);start=end-timedelta(days=30)
 records={e['id']:e for e in data['events'] if e['category']=='review' and e.get('published_at') and start<=datetime.fromisoformat(e['published_at'])<=end}
 themes=[]
 for key,title,tone,description,ids in THEMES:
  keys=ids.split();assert all(k in {e['id'] for e in data['events']} for k in keys)
  themes.append(dict(id=key,title=title,tone=tone,description=description,ids=[k for k in keys if k in records]))
 return dict(cutoff=data['generated_at'],reviewed_from=start.isoformat(),records=list(records.values()),themes=themes,method='人工按原文归类；每条记录在同一主题计一次，可同时进入多个主题。无明确感知、仅笼统好坏或无关内容不进入主题排名。同数并列，按最近提及时间展示，最多五类。')
