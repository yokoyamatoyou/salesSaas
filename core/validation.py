from typing import List
from .models import SalesInput

def validate_sales_input(input_data: SalesInput) -> List[str]:
    """SalesInputの包括的な検証"""
    errors = []
    
    # 基本フィールドの検証
    if not input_data.industry or not input_data.industry.strip():
        errors.append("業界は必須です")
    elif len(input_data.industry.strip()) < 2:
        errors.append("業界は2文字以上で入力してください")
    
    if not input_data.product or not input_data.product.strip():
        errors.append("商品・サービスは必須です")
    elif len(input_data.product.strip()) < 2:
        errors.append("商品・サービスは2文字以上で入力してください")
    
    if not input_data.stage or not input_data.stage.strip():
        errors.append("商談ステージは必須です")
    
    if not input_data.purpose or not input_data.purpose.strip():
        errors.append("目的は必須です")
    elif len(input_data.purpose.strip()) < 5:
        errors.append("目的は5文字以上で入力してください")
    
    # XORフィールドの検証
    xor_errors = validate_xor_fields(input_data)
    errors.extend(xor_errors)
    
    # 制約フィールドの検証
    if input_data.constraints:
        for i, constraint in enumerate(input_data.constraints):
            if not constraint or not constraint.strip():
                errors.append(f"制約{i+1}が空です")
            elif len(constraint.strip()) < 3:
                errors.append(f"制約{i+1}は3文字以上で入力してください")
    
    return errors

def validate_xor_fields(input_data: SalesInput) -> List[str]:
    """XORフィールドの検証（説明/URL、競合/URL）"""
    errors = []
    
    # 説明フィールドのXOR検証（入力された場合のみ）
    has_description = bool(input_data.description and input_data.description.strip())
    has_description_url = bool(input_data.description_url)
    
    if has_description and has_description_url:
        errors.append("説明はテキストまたはURLのいずれか一方を入力してください")
    
    # 競合フィールドのXOR検証（入力された場合のみ）
    has_competitor = bool(input_data.competitor and input_data.competitor.strip())
    has_competitor_url = bool(input_data.competitor_url)
    
    if has_competitor and has_competitor_url:
        errors.append("競合はテキストまたはURLのいずれか一方を入力してください")
    
    return errors

def validate_industry(industry: str) -> List[str]:
    """業界名の検証"""
    errors = []
    
    if not industry or not industry.strip():
        errors.append("業界は必須です")
        return errors
    
    industry = industry.strip()
    
    if len(industry) < 2:
        errors.append("業界は2文字以上で入力してください")
    
    if len(industry) > 100:
        errors.append("業界は100文字以下で入力してください")
    
    # 一般的な業界名のパターンチェック
    invalid_chars = ['<', '>', '&', '"', "'", '\\', '/']
    for char in invalid_chars:
        if char in industry:
            errors.append(f"業界名に無効な文字 '{char}' が含まれています")
            break
    
    return errors

def validate_product(product: str) -> List[str]:
    """商品・サービス名の検証"""
    errors = []
    
    if not product or not product.strip():
        errors.append("商品・サービスは必須です")
        return errors
    
    product = product.strip()
    
    if len(product) < 2:
        errors.append("商品・サービスは2文字以上で入力してください")
    
    if len(product) > 200:
        errors.append("商品・サービスは200文字以下で入力してください")
    
    return errors

def validate_stage(stage: str) -> bool:
    """商談ステージの検証"""
    valid_stages = ["初期接触", "ニーズ発掘", "提案", "商談", "クロージング"]
    return stage in valid_stages

def validate_purpose(purpose: str) -> List[str]:
    """目的の検証"""
    errors = []
    
    if not purpose or not purpose.strip():
        errors.append("目的は必須です")
        return errors
    
    purpose = purpose.strip()
    
    if len(purpose) < 5:
        errors.append("目的は5文字以上で入力してください")
    
    if len(purpose) > 500:
        errors.append("目的は500文字以下で入力してください")
    
    return errors

