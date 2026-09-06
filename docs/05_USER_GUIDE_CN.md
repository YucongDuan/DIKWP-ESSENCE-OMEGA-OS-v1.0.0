# 中文用户指南

## 1. 运行示例

```bash
PYTHONPATH=src python -m essence_omega_os run \
  examples/01_minimal_causal_kernel.json \
  --output outputs/my-run
```

## 2. 阅读输出的顺序

1. `essence_certificate.json`：最终有界证书；
2. `candidate_evaluations.json`：每个候选的失败位置；
3. `counterfactual_ablation_matrix.csv`：组件消融结果；
4. `essence_lattice.json`：候选之间的包含、等价、谱系和支配关系；
5. `residual_frontier.json`：仍未被当前本质拥有的内容；
6. `probe_plan.json`：下一项安全区别性探针；
7. `evidence_ledger.jsonl`：完整哈希事件链。

## 3. 自定义场景最低要求

必须至少提供：一个场景标识、一个测试、一个世界、一个候选、候选组成、预测、逐组成消融、反向再生和预先声明的反例条件。

## 4. 如何理解“认证”

`ESSENCE_CERTIFIED_WITHIN_DECLARED_SCOPE` 只表示候选在声明世界族和测试族中满足本系统的全部协议。它不是现实产品认证、临床认证、安全认证、意识认证或宇宙本体证明。
