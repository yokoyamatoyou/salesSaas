from typing import Dict, Any

def get_pre_advice_schema() -> Dict[str, Any]:
    """事前アドバイス出力のJSONスキーマ"""
    return {
        "type": "object",
        "properties": {
            "short_term": {
                "type": "object",
                "properties": {
                    "openers": {
                        "type": "object",
                        "properties": {
                            "call": {"type": "string"},
                            "visit": {"type": "string"},
                            "email": {"type": "string"}
                        },
                        "required": ["call", "visit", "email"]
                    },
                    "discovery": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "differentiation": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "vs": {"type": "string"},
                                "talk": {"type": "string"}
                            },
                            "required": ["vs", "talk"]
                        }
                    },
                    "objections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "script": {"type": "string"}
                            },
                            "required": ["type", "script"]
                        }
                    },
                    "next_actions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "kpi": {
                        "type": "object",
                        "properties": {
                            "next_meeting_rate": {"type": "string"},
                            "poc_rate": {"type": "string"}
                        },
                        "required": ["next_meeting_rate", "poc_rate"]
                    },
                    "summary": {"type": "string"}
                },
                "required": ["openers", "discovery", "differentiation", "objections", "next_actions", "kpi", "summary"]
            },
            "mid_term": {
                "type": "object",
                "properties": {
                    "plan_weeks_4_12": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["plan_weeks_4_12"]
            }
        },
        "required": ["short_term", "mid_term"]
    }

def get_post_review_schema() -> Dict[str, Any]:
    """商談後ふりかえり出力のJSONスキーマ"""
    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "bant": {
                "type": "object",
                "properties": {
                    "budget": {"type": "string"},
                    "authority": {"type": "string"},
                    "need": {"type": "string"},
                    "timeline": {"type": "string"}
                },
                "required": ["budget", "authority", "need", "timeline"]
            },
            "champ": {
                "type": "object",
                "properties": {
                    "challenges": {"type": "string"},
                    "authority": {"type": "string"},
                    "money": {"type": "string"},
                    "prioritization": {"type": "string"}
                },
                "required": ["challenges", "authority", "money", "prioritization"]
            },
            "objections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string"},
                        "details": {"type": "string"},
                        "counter": {"type": "string"}
                    },
                    "required": ["theme", "details", "counter"]
                }
            },
            "risks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "prob": {"type": "string"},
                        "reason": {"type": "string"},
                        "mitigation": {"type": "string"}
                    },
                    "required": ["type", "prob", "reason", "mitigation"]
                }
            },
            "next_actions": {
                "type": "array",
                "items": {"type": "string"}
            },
            "followup_email": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["subject", "body"]
            },
            "metrics_update": {
                "type": "object",
                "properties": {
                    "stage": {"type": "string"},
                    "win_prob_delta": {"type": "string"}
                },
                "required": ["stage", "win_prob_delta"]
            }
        },
        "required": ["summary", "bant", "champ", "objections", "risks", "next_actions", "followup_email", "metrics_update"]
    }

