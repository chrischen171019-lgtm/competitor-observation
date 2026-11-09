TOPICS=[
('wb-speed','workbuddy','问题反馈','等待回复与任务执行卡顿','执行任务或简单提问，希望得到及时、可预期的反馈。',['090af1dc713d1cbc2ff676ef','19cea335d5f5420f336f7e97','f408cffb7ac8e4f552a95b99']),
('wb-sync','workbuddy','问题反馈','手机与电脑之间的消息衔接','跨设备继续任务；评论提及无法同步，条件未核实。',['1f067d884b6df42a0741d405']),
('wb-supplement','workbuddy','功能诉求','Agent 执行中补充要求','发出指令后仍需补充要求；用户称手机端与电脑端不同。',['e538a9dd3b6d5c951df02964']),
('wb-app','workbuddy','使用体验','应用制作获得肯定，更新入口存在疑问','制作小程序与应用，并希望持续更新使用；保留同一评论中的正反体验。',['ab3038bfdd70201007a9cc67']),
('db-companion','doubao','使用体验','情绪陪伴与被理解的感受','在交流中获得理解和情绪回应；不代表长期效果。',['023b86ee6f14c589ee35d9a9','08d8a001de97e063523e0871']),
('db-writing','doubao','使用体验','原作润色得到认可','改善已有文字表达；没有原稿与输出供独立比较。',['0ce1465439291e139ced0c43']),
('db-accuracy','doubao','问题反馈','答题与翻译准确性反馈','希望答题和翻译结果可用；缺少具体输入输出，不能估计准确率。',['91cfbe6ddf7bcde0c85e5040','cbaf6eba7c57d3bd9b99f574']),
('db-agent','doubao','功能诉求','希望恢复智能体功能','依赖智能体交流，希望保持使用入口；不据此确认功能下线。',['2cba01dbecbc943c4579cfde']),
('wk-snippet','weknora','缺陷报告','Unicode 处理可能影响检索片段','提交者仅在源码层复现，明确未在部署服务或真实用户会话中观察到。',['d4d8b489d4f54c35b727228c'])]
def make_feedback(data):
 byid={e['id']:e for e in data['events']};items=[]
 for key,product,kind,title,goal,ids in TOPICS:
  rows=[byid[i] for i in ids];assert all(e['product']==product for e in rows)
  items.append(dict(id=key,product=product,kind=kind,title=title,goal=goal,source='github' if kind=='缺陷报告' else 'apple',evidence=rows))
 return dict(cutoff=data['generated_at'],topics=items)
