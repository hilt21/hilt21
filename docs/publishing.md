# Publishing Guide

这份主页遵循一个明确边界：人负责选择与判断，Codex 可以协助写作，Profile Publisher 只做确定性发布。

## 从记忆到公开记录

1. 只读取与当前主题有关的 Codex 记忆，不复制完整用户画像、会话日志或内部项目资料。
2. 将可复用的经历匿名提炼为本地草稿，固定写清“问题、实验、认识、下一个问题”。
3. 草稿保存在被 Git 忽略的本地目录；隐藏或不渲染的公开文件不算隐私边界。
4. 由主页所有者逐字审核标题、摘要、正文、日期和公开范围。
5. 只有明确批准的版本才能进入公开探索记录目录，且状态必须为 `approved`。
6. 在本地运行完整黑盒测试和 Profile Publisher，检查生成结果与 Git diff。
7. 提交已批准素材。GitHub Actions 随后重新生成主页与完整索引；输出不变时不创建 bot commit。

## 记录契约

每条公开记录使用最小 metadata：

- `title`: 公开标题；
- `date`: 实际批准或发布日期，格式为 `YYYY-MM-DD`；
- `summary`: 一句话摘要；
- `status`: 必须为 `approved`。

记录文件名使用小写英文字母、数字和单个连字符组成的稳定标识，例如
`durable-memory.md`。文件名也会进入公开链接，并接受私密词检查。

正文必须按顺序且只出现一次：

1. `问题`
2. `实验`
3. `认识`
4. `下一个问题`

## 隐私检查

发布器会阻止常见本地路径、home 路径、疑似访问令牌、私钥头和邮箱。额外私密词通过 `PROFILE_PRIVATE_TERMS` 注入，禁止写进公开仓库或错误日志。

GitHub Actions 可从同名 repository secret 读取私密词。没有配置该 secret 时，通用规则仍然生效。

自动检查只能拦截已知模式，不能代替人工语义审核。

## 生成页面

根 Profile README 与完整探索索引都是 Generated Surfaces，不应直接编辑。需要改变稳定文案时编辑模板；需要改变探索内容时编辑对应的已批准记录。

生成器按发布日期倒序排列记录，同日按文件标识升序；主页展示前三篇，完整索引保留全部记录。主页的“当前问题”和“最近更新”均取自排序后的第一篇记录。

## 本地验证

```bash
/usr/bin/python3 -m unittest -v tests/test_build_profile.py
/usr/bin/python3 scripts/build_profile.py --root .
```

运行后只应出现两个 Generated Surfaces 的变化。若失败，先修复素材或规则，不要绕过隐私检查。
