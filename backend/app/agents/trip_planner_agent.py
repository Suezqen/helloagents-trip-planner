"""多智能体旅行规划系统"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List

from hello_agents import SimpleAgent

from ..models.schemas import Attraction, DayPlan, Hotel, Location, Meal, TripPlan, TripRequest, WeatherInfo
from ..services.amap_service import get_amap_mcp_tool
from ..services.llm_service import get_llm

# ============ Agent提示词 ============

ATTRACTION_AGENT_PROMPT = """你是景点搜索专家。你的任务是根据城市和用户偏好搜索合适的景点。

**重要提示:**
你必须使用工具来搜索景点!不要自己编造景点信息!

**工具调用格式:**
使用maps_text_search工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=景点关键词,city=城市名]`

**示例:**
用户: "搜索北京的历史文化景点"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=历史文化,city=北京]

用户: "搜索上海的公园"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=公园,city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 参数用逗号分隔
"""

WEATHER_AGENT_PROMPT = """你是天气查询专家。你的任务是查询指定城市的天气信息。

**重要提示:**
你必须使用工具来查询天气!不要自己编造天气信息!

**工具调用格式:**
使用maps_weather工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_weather:city=城市名]`

**示例:**
用户: "查询北京天气"
你的回复: [TOOL_CALL:amap_maps_weather:city=北京]

用户: "上海的天气怎么样"
你的回复: [TOOL_CALL:amap_maps_weather:city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
"""

HOTEL_AGENT_PROMPT = """你是酒店推荐专家。你的任务是根据城市和景点位置推荐合适的酒店。

**重要提示:**
你必须使用工具来搜索酒店!不要自己编造酒店信息!

**工具调用格式:**
使用maps_text_search工具搜索酒店时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=酒店,city=城市名]`

**示例:**
用户: "搜索北京的酒店"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=酒店,city=北京]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 关键词使用"酒店"或"宾馆"
"""

PLANNER_AGENT_PROMPT = """你是行程规划专家。你的任务是根据景点信息和天气信息,生成详细的旅行计划。

请严格按照以下JSON格式返回旅行计划:
```json
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50},
        {"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

**重要提示:**
1. weather_info数组必须包含每一天的天气信息
2. 温度必须是纯数字(不要带°C等单位)
3. 每天安排2-3个景点
4. 考虑景点之间的距离和游览时间
5. 每天必须包含早中晚三餐
6. 提供实用的旅行建议
7. **必须包含预算信息**:
   - 景点门票价格(ticket_price)
   - 餐饮预估费用(estimated_cost)
   - 酒店预估费用(estimated_cost)
   - 预算汇总(budget)包含各项总费用
"""


class MultiAgentTripPlanner:
    """多智能体旅行规划系统"""

    def __init__(self):
        """初始化多智能体系统"""
        print("🔄 开始初始化多智能体旅行规划系统...")

        try:
            self.llm = get_llm()

            print("  - 复用共享MCP工具...")
            self.amap_tool = get_amap_mcp_tool()

            print("  - 创建景点搜索Agent...")
            self.attraction_agent = SimpleAgent(
                name="景点搜索专家",
                llm=self.llm,
                system_prompt=ATTRACTION_AGENT_PROMPT,
            )
            self.attraction_agent.add_tool(self.amap_tool)

            print("  - 创建天气查询Agent...")
            self.weather_agent = SimpleAgent(
                name="天气查询专家",
                llm=self.llm,
                system_prompt=WEATHER_AGENT_PROMPT,
            )
            self.weather_agent.add_tool(self.amap_tool)

            print("  - 创建酒店推荐Agent...")
            self.hotel_agent = SimpleAgent(
                name="酒店推荐专家",
                llm=self.llm,
                system_prompt=HOTEL_AGENT_PROMPT,
            )
            self.hotel_agent.add_tool(self.amap_tool)

            print("  - 创建行程规划Agent...")
            self.planner_agent = SimpleAgent(
                name="行程规划专家",
                llm=self.llm,
                system_prompt=PLANNER_AGENT_PROMPT,
            )

            print("✅ 多智能体系统初始化成功")
            print(f"   景点搜索Agent: {len(self.attraction_agent.list_tools())} 个工具")
            print(f"   天气查询Agent: {len(self.weather_agent.list_tools())} 个工具")
            print(f"   酒店推荐Agent: {len(self.hotel_agent.list_tools())} 个工具")

        except Exception as e:
            print(f"❌ 多智能体系统初始化失败: {str(e)}")
            import traceback

            traceback.print_exc()
            raise

    def plan_trip(self, request: TripRequest) -> TripPlan:
        """使用多智能体协作生成旅行计划"""
        try:
            print(f"\n{'=' * 60}")
            print("🚀 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"{'=' * 60}\n")

            print("📍 步骤1: 搜索景点...")
            attraction_query = self._build_attraction_query(request)
            attraction_response = self.attraction_agent.run(attraction_query)
            print(f"景点搜索结果: {attraction_response[:200]}...\n")

            print("🌤️  步骤2: 查询天气...")
            weather_query = self._build_weather_query(request)
            weather_response = self.weather_agent.run(weather_query)
            print(f"天气查询结果: {weather_response[:200]}...\n")

            print("🏨 步骤3: 搜索酒店...")
            hotel_query = self._build_hotel_query(request)
            hotel_response = self.hotel_agent.run(hotel_query)
            print(f"酒店搜索结果: {hotel_response[:200]}...\n")

            print("📋 步骤4: 生成行程计划...")
            planner_query = self._build_planner_query(request, attraction_response, weather_response, hotel_response)
            planner_response = self.planner_agent.run(planner_query)
            print(f"行程规划结果: {planner_response[:300]}...\n")

            trip_plan = self._parse_response(planner_response, request)

            print(f"{'=' * 60}")
            print("✅ 旅行计划生成完成!")
            print(f"{'=' * 60}\n")

            return trip_plan

        except Exception as e:
            print(f"❌ 生成旅行计划失败: {str(e)}")
            import traceback

            traceback.print_exc()
            return self._create_fallback_plan(request)

    def _build_attraction_query(self, request: TripRequest) -> str:
        """构建景点搜索查询 - 直接包含工具调用"""
        if request.preferences:
            keywords = request.preferences[0]
        else:
            keywords = "景点"

        return (
            f"请使用amap_maps_text_search工具搜索{request.city}的{keywords}相关景点。"
            f"\n[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        )

    def _build_weather_query(self, request: TripRequest) -> str:
        """构建天气查询请求"""
        return (
            f"请查询{request.city}从{request.start_date}到{request.end_date}附近几天的天气趋势。"
            f"\n[TOOL_CALL:amap_maps_weather:city={request.city}]"
        )

    def _build_hotel_query(self, request: TripRequest) -> str:
        """构建酒店搜索请求"""
        hotel_keyword = request.accommodation or "酒店"
        return (
            f"请搜索{request.city}适合{hotel_keyword}偏好的住宿选择。"
            f"\n[TOOL_CALL:amap_maps_text_search:keywords={hotel_keyword},city={request.city}]"
        )

    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "") -> str:
        """构建行程规划查询"""
        query = f"""请根据以下信息生成{request.city}的{request.travel_days}天旅行计划:

**基本信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通方式: {request.transportation}
- 住宿: {request.accommodation}
- 偏好: {', '.join(request.preferences) if request.preferences else '无'}

**景点信息:**
{attractions}

**天气信息:**
{weather}

**酒店信息:**
{hotels}

**要求:**
1. 每天安排2-3个景点
2. 每天必须包含早中晚三餐
3. 每天推荐一个具体的酒店(从酒店信息中选择)
4. 考虑景点之间的距离和交通方式
5. 返回完整的JSON格式数据
6. 景点的经纬度坐标要真实准确
"""
        if request.free_text_input:
            query += f"\n**额外要求:** {request.free_text_input}"

        return query

    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """解析Agent响应"""
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("响应中未找到JSON数据")

            data = json.loads(json_str)
            normalized_data = self._normalize_plan_data(data, request)
            return TripPlan(**normalized_data)

        except Exception as e:
            print(f"⚠️  解析响应失败: {str(e)}")
            print("   将使用备用方案生成计划")
            return self._create_fallback_plan(request)

    def _normalize_plan_data(self, data: Dict[str, Any], request: TripRequest) -> Dict[str, Any]:
        """对模型返回结果进行标准化处理"""
        normalized = dict(data)
        normalized["city"] = normalized.get("city") or request.city
        normalized["start_date"] = normalized.get("start_date") or request.start_date
        normalized["end_date"] = normalized.get("end_date") or request.end_date
        normalized["days"] = self._normalize_days(normalized.get("days"), request)
        normalized["weather_info"] = self._normalize_weather(normalized.get("weather_info"), request)
        normalized["overall_suggestions"] = (
            normalized.get("overall_suggestions")
            or f"建议优先确认热门景点预约时间，并按{request.transportation}方式预留城市内通勤时间。"
        )
        normalized["budget"] = self._normalize_budget(normalized.get("budget"), normalized["days"], request)
        return normalized

    def _normalize_days(self, days: Any, request: TripRequest) -> List[Dict[str, Any]]:
        """补齐每日行程字段"""
        if not isinstance(days, list) or not days:
            return [day.model_dump() for day in self._create_fallback_plan(request).days]

        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        normalized_days: List[Dict[str, Any]] = []

        for index in range(request.travel_days):
            current_date = (start_date + timedelta(days=index)).strftime("%Y-%m-%d")
            raw_day = days[index] if index < len(days) and isinstance(days[index], dict) else {}

            attractions = raw_day.get("attractions")
            if not isinstance(attractions, list) or not attractions:
                attractions = [
                    {
                        "name": f"{request.city}景点{index + 1}",
                        "address": f"{request.city}市区待补充",
                        "location": {"longitude": 116.4 + index * 0.01, "latitude": 39.9 + index * 0.01},
                        "visit_duration": 120,
                        "description": f"{request.city}景点推荐",
                        "category": "景点",
                        "ticket_price": 0,
                    }
                ]

            meals = raw_day.get("meals")
            if not isinstance(meals, list):
                meals = []

            normalized_meals = []
            existing_meals = {meal.get("type"): meal for meal in meals if isinstance(meal, dict)}
            for meal_type, meal_name in (
                ("breakfast", "早餐"),
                ("lunch", "午餐"),
                ("dinner", "晚餐"),
            ):
                meal = dict(existing_meals.get(meal_type) or {})
                meal["type"] = meal_type
                meal["name"] = meal.get("name") or f"第{index + 1}天{meal_name}"
                meal["description"] = meal.get("description") or f"建议在景点周边安排{meal_name}"
                meal["estimated_cost"] = int(meal.get("estimated_cost") or 0)
                normalized_meals.append(meal)

            hotel = raw_day.get("hotel")
            if not isinstance(hotel, dict):
                hotel = {
                    "name": f"{request.city}{request.accommodation}",
                    "address": f"{request.city}市中心区域",
                    "type": request.accommodation,
                    "price_range": "待确认",
                    "rating": "",
                    "distance": "建议控制在主要景点 3 公里内",
                    "estimated_cost": 0,
                }

            normalized_days.append(
                {
                    "date": raw_day.get("date") or current_date,
                    "day_index": raw_day.get("day_index", index),
                    "description": raw_day.get("description") or f"第{index + 1}天行程安排",
                    "transportation": raw_day.get("transportation") or request.transportation,
                    "accommodation": raw_day.get("accommodation") or request.accommodation,
                    "hotel": hotel,
                    "attractions": attractions[:3],
                    "meals": normalized_meals,
                }
            )

        return normalized_days

    def _normalize_weather(self, weather_info: Any, request: TripRequest) -> List[Dict[str, Any]]:
        """确保天气数组与天数对齐"""
        if not isinstance(weather_info, list):
            weather_info = []

        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        normalized_weather: List[Dict[str, Any]] = []

        for index in range(request.travel_days):
            current_date = (start_date + timedelta(days=index)).strftime("%Y-%m-%d")
            raw_weather = weather_info[index] if index < len(weather_info) and isinstance(weather_info[index], dict) else {}
            normalized_weather.append(
                {
                    "date": raw_weather.get("date") or current_date,
                    "day_weather": raw_weather.get("day_weather") or "以实时天气为准",
                    "night_weather": raw_weather.get("night_weather") or "以实时天气为准",
                    "day_temp": raw_weather.get("day_temp", 0),
                    "night_temp": raw_weather.get("night_temp", 0),
                    "wind_direction": raw_weather.get("wind_direction") or "",
                    "wind_power": raw_weather.get("wind_power") or "",
                }
            )

        return normalized_weather

    def _normalize_budget(self, budget: Any, days: List[Dict[str, Any]], request: TripRequest) -> Dict[str, int]:
        """汇总预算字段"""
        total_attractions = sum(
            int(attraction.get("ticket_price") or 0)
            for day in days
            for attraction in day.get("attractions", [])
            if isinstance(attraction, dict)
        )
        total_hotels = sum(
            int((day.get("hotel") or {}).get("estimated_cost") or 0)
            for day in days
            if isinstance(day.get("hotel"), dict)
        )
        total_meals = sum(
            int(meal.get("estimated_cost") or 0)
            for day in days
            for meal in day.get("meals", [])
            if isinstance(meal, dict)
        )

        default_transportation = self._estimate_transportation_budget(request)
        if isinstance(budget, dict):
            total_transportation = int(budget.get("total_transportation") or default_transportation)
        else:
            total_transportation = default_transportation

        total = total_attractions + total_hotels + total_meals + total_transportation
        budget_dict = budget if isinstance(budget, dict) else {}
        return {
            "total_attractions": int(budget_dict.get("total_attractions") or total_attractions),
            "total_hotels": int(budget_dict.get("total_hotels") or total_hotels),
            "total_meals": int(budget_dict.get("total_meals") or total_meals),
            "total_transportation": total_transportation,
            "total": int(budget_dict.get("total") or total),
        }

    def _estimate_transportation_budget(self, request: TripRequest) -> int:
        """按交通方式估算城市内交通费用"""
        base_map = {
            "步行": 20,
            "公共交通": 40,
            "自驾": 180,
            "混合": 80,
        }
        return base_map.get(request.transportation, 60) * request.travel_days

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当Agent失败时)"""
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i + 1}天行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}景点{j + 1}",
                        address=f"{request.city}市",
                        location=Location(longitude=116.4 + i * 0.01 + j * 0.005, latitude=39.9 + i * 0.01 + j * 0.005),
                        visit_duration=120,
                        description=f"这是{request.city}的著名景点",
                        category="景点",
                        ticket_price=0,
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"第{i + 1}天早餐", description="当地特色早餐", estimated_cost=25),
                    Meal(type="lunch", name=f"第{i + 1}天午餐", description="午餐推荐", estimated_cost=55),
                    Meal(type="dinner", name=f"第{i + 1}天晚餐", description="晚餐推荐", estimated_cost=80),
                ],
                hotel=Hotel(
                    name=f"{request.city}{request.accommodation}",
                    address=f"{request.city}核心区域",
                    type=request.accommodation,
                    price_range="待确认",
                    rating="",
                    distance="距主要景点约2公里",
                    estimated_cost=260 if request.accommodation == "经济型酒店" else 420,
                ),
            )
            days.append(day_plan)

        weather_info = [
            WeatherInfo(
                date=(start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                day_weather="以实时天气为准",
                night_weather="以实时天气为准",
                day_temp=0,
                night_temp=0,
                wind_direction="",
                wind_power="",
            )
            for i in range(request.travel_days)
        ]

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=weather_info,
            overall_suggestions=f"这是为您规划的{request.city}{request.travel_days}日游行程,建议提前查看各景点的开放时间。",
            budget=self._normalize_budget({}, [day.model_dump() for day in days], request),
        )


_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(单例模式)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner
