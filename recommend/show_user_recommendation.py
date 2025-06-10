from recbole.quick_start import load_data_and_model
import torch

# ====== 用户自定义参数 ======
# 模型文件路径（请根据实际情况修改）
model_file = 'saved/BPR-Jun-10-2025_17-46-38.pth'
# 指定要查看的用户原始ID（如1）
user_raw_id = 1
# 推荐TopK个物品
topk = 10

# ====== 加载模型和数据 ======
config, model, dataset, train_data, valid_data, test_data = load_data_and_model(model_file)

# ====== 获取用户内部ID ======
uid = dataset.token2id(dataset.uid_field, [str(user_raw_id)])[0]

# ====== 构造用户输入，获取所有物品的分数 ======
user_tensor = torch.tensor([uid])
item_tensor = torch.arange(dataset.item_num)
model.eval()
with torch.no_grad():
    scores = model.full_sort_predict({'user_id': user_tensor, 'item_id': item_tensor})
    print("scores:", scores)
    # 取实际物品数和topk的较小值，防止K大于物品数
    real_topk = min(topk, dataset.item_num)
    topk_scores, topk_indices = torch.topk(scores, k=real_topk)
    # 去重并只保留前topk个不同的物品
    seen = set()
    unique_indices = []
    for idx in topk_indices.tolist():
        if idx not in seen:
            seen.add(idx)
            unique_indices.append(idx)
        if len(unique_indices) >= topk:
            break
    topk_indices = unique_indices

recommended_items = list(dataset.id2token(dataset.iid_field, topk_indices))
print(f"用户 {user_raw_id} 推荐的Top{topk}物品ID：", recommended_items)


# ====== 获取该用户在测试集的真实喜欢物品 ======
test_inter = test_data.dataset.inter_feat
user_mask = test_inter['user_id'] == uid  # 用内部ID
user_test_items = list(dataset.id2token(dataset.iid_field, test_inter['item_id'][user_mask].tolist()))
print(f"用户 {user_raw_id} 在测试集真实喜欢的物品ID：", user_test_items)

# ====== 对比命中情况 ======
hit_items = set(recommended_items) & set(user_test_items)
print(f"命中的物品ID：", list(hit_items))
print(f"命中个数：{len(hit_items)}/{topk}") 