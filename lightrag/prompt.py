from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["organization", "person", "geo", "event", "category"]

PROMPTS["entity_extraction"] = """-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, Refers to function definitions or function calls, Does not include class definition. use same language as input text. If English, capitalized the name. For example, the code from testing.utils.unit_test_prebuild_tool import UnitTestPrebuildTool\nUnitTestPrebuildTool.create_alarm_log() is represented as TESTING.UTILS.UNIT_TEST_PREBUILD_TOOL:UNITTESTPREBUILDTOOL.create_alarm_log
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format entity_name as <package:class.function>
If there is no class name format as <package:function>
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other. Refers to function call relationships.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
-Examples-
######################
Example 1:

Entity_types: [function]
Text:
"<code-block code-path=\"risk_qualitative\\qualitative.py\">\n<code>\nimport logging\nfrom threading import Thread\nfrom risk_qualitative.util.utils import Config\nfrom risk_qualitative.util.pulsar_util import get_pulsar_consumer, get_pulsar_producer\nfrom risk_qualitative.schemas.pulsar.config import DataSecurityLogProducerName\nfrom risk_qualitative.schemas.pulsar.config import PulsarConfig\n\nclass RiskQualitative:\n    def run(self):\n        logging.info(f\"prepare receive risk_data_security_log message...\")\n        works_num = Config[\"base\"][\"works_num\"]\n        consumer = get_pulsar_consumer(\n            port=PulsarConfig.port,\n            host=PulsarConfig.host,\n            topic=DataSecurityLogProducerName.dsp_data_security_log_produces_name,\n            subscribe_name=\"risk_qualitative_consumer\",\n            authentication=PulsarConfig.authentication\n        )\n        producer = get_pulsar_producer(\n            port=PulsarConfig.port,\n            host=PulsarConfig.host,\n            authentication=PulsarConfig.authentication\n        )\n        self.get_data_from_pulsar(consumer)\n        for i in range(works_num):\n            Thread(target=self.worker, args=(i, producer,), daemon=True).start()\n        while True:\n            self.get_data_from_pulsar(consumer)\n            inactive = HeartbeatMonitor.check_inactive()\n            if inactive is True:\n                break\n            time.sleep(60)\n        return\n<code>\n<code-block>"
################
Output:
("entity"{tuple_delimiter}"risk_qualitative/qualitative:RiskQualitative.run"{tuple_delimiter}"function"{tuple_delimiter}"RiskQualitative.run is a function definition"){record_delimiter}
("entity"{tuple_delimiter}"risk_qualitative/util/pulsar_util:get_pulsar_consumer"{tuple_delimiter}"function"{tuple_delimiter}"get_pulsar_consumer is the called function"){record_delimiter}
("entity"{tuple_delimiter}"risk_qualitative/util/pulsar_util:get_pulsar_producer"{tuple_delimiter}"function"{tuple_delimiter}"get_pulsar_producer is the called function"){record_delimiter}
("entity"{tuple_delimiter}"risk_qualitative/qualitative:RiskQualitative.get_data_from_pulsar"{tuple_delimiter}"function"{tuple_delimiter}"RiskQualitative.get_data_from_pulsar is the called function"){record_delimiter}
("entity"{tuple_delimiter}"risk_qualitative/qualitative:HeartbeatMonitor.check_inactive"{tuple_delimiter}"function"{tuple_delimiter}"HeartbeatMonitor.check_inactive is the called function"){record_delimiter}
("relationship"{tuple_delimiter}"risk_qualitative/qualitative:RiskQualitative.run"{tuple_delimiter}"risk_qualitative/util/pulsar_util.get_pulsar_consumer"{tuple_delimiter}"RiskQualitative.run calls get_pulsar_consumer ."{tuple_delimiter}"RiskQualitative.run, get_pulsar_consumer, risk_qualitative/util/pulsar_util"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"risk_qualitative/qualitative:RiskQualitative.run"{tuple_delimiter}"risk_qualitative/util/pulsar_util.get_pulsar_producer"{tuple_delimiter}"RiskQualitative.run calls get_pulsar_producer ."{tuple_delimiter}"RiskQualitative.run, get_pulsar_producer, risk_qualitative/util/pulsar_util"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"risk_qualitative/qualitative:RiskQualitative.run"{tuple_delimiter}"risk_qualitative/qualitative/RiskQualitative.get_data_from_pulsar"{tuple_delimiter}"RiskQualitative.run calls RiskQualitative.get_data_from_pulsar ."{tuple_delimiter}"RiskQualitative.run, RiskQualitative.get_data_from_pulsar"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"risk_qualitative/qualitative:RiskQualitative.run"{tuple_delimiter}"risk_qualitative/qualitative/HeartbeatMonitor.check_inactive"{tuple_delimiter}"RiskQualitative.run calls HeartbeatMonitor.check_inactive ."{tuple_delimiter}"RiskQualitative.run, HeartbeatMonitor.check_inactive"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"RiskQualitative.run, get_pulsar_consumer, get_pulsar_producer, RiskQualitative.get_data_from_pulsar, HeartbeatMonitor.check_inactive, risk_qualitative/util/pulsar_util"){completion_delimiter}
#############################
Example 2:

Entity_types: [function]
Text:
"<code-block code-path=\"task_actuator\\main.go\">\n<code>\n```go\nimport (\n\t\"GPUTASKD/pkg/logger\"\n\t\"GPUTASKD/task_actuator/middleware\"\n\t\"GPUTASKD/task_actuator/internal/router\"\n\t\"GPUTASKD/pkg\"\n\t\"errors\"\n\t\"fmt\"\n\t\"github.com/gin-gonic/gin\"\n\t\"net/http\"\n\t\"time\"\n)\n\nfunc main() {{\n\t// 初始化日志\n\tif err := logger.InitInnerLogger(\"dspm_task_gpu\", \"task_actuator\"); err != nil {{\n\t\tfmt.Printf(\"InitInnerLogger err: %v\", err)\n\t\treturn\n\t}}\n\tinitApexConnector()\n\t// 初始化 HTTP 服务\n\tgin.SetMode(gin.ReleaseMode)\n\t// 全局中间件配置\n\thttpEngine := gin.New()\n\thttpEngine.Use(gin.Recovery())                                     // 异常处置中间件\n\thttpEngine.Use(middleware.TimeoutMiddleware(5 * 60 * time.Second)) // 请求超时中间件\n\thttpEngine.Use(middleware.GinLoggerHandler())                      // 日志中间件\n\t// 注册路由\n\trouter.RegisterRouter(httpEngine)\n\n\t// 启动服务\n\tserver := &http.Server{{\n\t\tAddr:    pkg.SvcActuatorUrl,\n\t\tHandler: httpEngine,\n\t}}\n\tif err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {{\n\t\tlogger.Error(\"http server startup err: %v\", err)\n\t\treturn\n\t}}\n\tlogger.Info(\"http server startup success\")\n}}\n```\n<code>\n<explain>## 整体功能\n该 Go 代码的主要功能是初始化并启动一个 HTTP 服务器。具体步骤包括：\n1. 初始化日志系统。\n2. 初始化 Apex 连接器。\n3. 配置 Gin 框架的全局中间件。\n4. 注册路由。\n5. 启动 HTTP 服务器，并监听指定的地址和端口。\n\n## 使用到的函数/类方法的作用\n- `logger.InitInnerLogger`: 初始化日志系统。\n- `initApexConnector`: 初始化 Apex 连接器。\n- `gin.SetMode`: 设置 Gin 框架的运行模式。\n- `gin.New`: 创建一个新的 Gin 引擎实例。\n- `httpEngine.Use`: 注册中间件。\n- `router.RegisterRouter`: 注册路由。\n- `http.Server`: 创建一个 HTTP 服务器。\n- `server.ListenAndServe`: 启动 HTTP 服务器。\n- `logger.Error`: 记录错误日志。\n- `logger.Info`: 记录信息日志。\n\n## 逐行解释功能\n```go\nimport (\n\t\"GPUTASKD/pkg/logger\" // 引入日志模块\n\t\"GPUTASKD/task_actuator/middleware\" // 引入中间件模块\n\t\"GPUTASKD/task_actuator/internal/router\" // 引入路由模块\n\t\"GPUTASKD/pkg\" // 引入包模块\n\t\"errors\" // 引入错误处理模块\n\t\"fmt\" // 引入格式化输入输出模块\n\t\"github.com/gin-gonic/gin\" // 引入 Gin 框架\n\t\"net/http\" // 引入 HTTP 模块\n\t\"time\" // 引入时间模块\n)\n\nfunc main() {{\n\t// 初始化日志\n\tif err := logger.InitInnerLogger(\"dspm_task_gpu\", \"task_actuator\"); err != nil {{\n\t\tfmt.Printf(\"InitInnerLogger err: %v\", err) // 如果初始化日志失败，打印错误信息\n\t\treturn // 退出程序\n\t}}\n\tinitApexConnector() // 初始化 Apex 连接器\n\t// 初始化 HTTP 服务\n\tgin.SetMode(gin.ReleaseMode) // 设置 Gin 框架的运行模式为发布模式\n\t// 全局中间件配置\n\thttpEngine := gin.New() // 创建一个新的 Gin 引擎实例\n\thttpEngine.Use(gin.Recovery()) // 注册异常处置中间件，用于捕获并处理 panic\n\thttpEngine.Use(middleware.TimeoutMiddleware(5 * 60 * time.Second)) // 注册请求超时中间件，设置超时时间为 5 分钟\n\thttpEngine.Use(middleware.GinLoggerHandler()) // 注册日志中间件，记录请求日志\n\t// 注册路由\n\trouter.RegisterRouter(httpEngine) // 注册路由到 Gin 引擎\n\t// 启动服务\n\tserver := &http.Server{{\n\t\tAddr:    pkg.SvcActuatorUrl, // 设置服务器监听的地址和端口\n\t\tHandler: httpEngine, // 设置处理请求的 handler\n\t}}\n\tif err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {{\n\t\tlogger.Error(\"http server startup err: %v\", err) // 如果启动失败，记录错误日志\n\t\treturn // 退出程序\n\t}}\n\tlogger.Info(\"http server startup success\") // 记录启动成功的日志\n}}\n```<explain>\n<code-block>"
#############
Output:
("entity"{tuple_delimiter}"task_actuator/main:main"{tuple_delimiter}"function"{tuple_delimiter}"main is a function definition."){record_delimiter}
("entity"{tuple_delimiter}"task_actuator/main:initApexConnector"{tuple_delimiter}"function"{tuple_delimiter}"initApexConnector is the called function."){record_delimiter}
("entity"{tuple_delimiter}"GPUTASKD/task_actuator/middleware:TimeoutMiddleware"{tuple_delimiter}"function"{tuple_delimiter}"TimeoutMiddleware is the called function."){record_delimiter}
("entity"{tuple_delimiter}"GPUTASKD/task_actuator/middleware:GinLoggerHandler"{tuple_delimiter}"function"{tuple_delimiter}"GinLoggerHandler is the called function."){record_delimiter}
("entity"{tuple_delimiter}"GPUTASKD/task_actuator/internal/router:RegisterRouter"{tuple_delimiter}"function"{tuple_delimiter}"RegisterRouter is the called function."){record_delimiter}
("relationship"{tuple_delimiter}"task_actuator/main:main"{tuple_delimiter}"task_actuator/main:initApexConnector"{tuple_delimiter}"main calls initApexConnector."{tuple_delimiter}"main, initApexConnector, task_actuator/main, GPUTASKD/task_actuator/middleware"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"task_actuator/main:main"{tuple_delimiter}"GPUTASKD/task_actuator/middleware:TimeoutMiddleware"{tuple_delimiter}"main calls TimeoutMiddleware."{tuple_delimiter}"main, TimeoutMiddleware, task_actuator/main, GPUTASKD/task_actuator/middleware"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"task_actuator/main:main"{tuple_delimiter}"GPUTASKD/task_actuator/middleware:GinLoggerHandler"{tuple_delimiter}"main calls GinLoggerHandler."{tuple_delimiter}"main, GinLoggerHandler, task_actuator/main, GPUTASKD/task_actuator/middleware"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"task_actuator/main:main"{tuple_delimiter}"GPUTASKD/task_actuator/internal/router:RegisterRouter"{tuple_delimiter}"main calls RegisterRouter."{tuple_delimiter}"main, RegisterRouter, task_actuator/main, GPUTASKD/task_actuator/internal/router"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"main, initApexConnector, TimeoutMiddleware, GinLoggerHandler, RegisterRouter, task_actuator/main, GPUTASKD/task_actuator/middleware, GPUTASKD/task_actuator/internal/router"){completion_delimiter}
#############################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [person, technology, mission, organization, location]
Text:
```
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
```

Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
#############################""",
    """Example 2:

Entity_types: [company, index, commodity, market_trend, economic_policy, biological]
Text:
```
Stock markets faced a sharp downturn today as tech giants saw significant declines, with the Global Tech Index dropping by 3.4% in midday trading. Analysts attribute the selloff to investor concerns over rising interest rates and regulatory uncertainty.

Among the hardest hit, Nexon Technologies saw its stock plummet by 7.8% after reporting lower-than-expected quarterly earnings. In contrast, Omega Energy posted a modest 2.1% gain, driven by rising oil prices.

Meanwhile, commodity markets reflected a mixed sentiment. Gold futures rose by 1.5%, reaching $2,080 per ounce, as investors sought safe-haven assets. Crude oil prices continued their rally, climbing to $87.60 per barrel, supported by supply constraints and strong demand.

Financial experts are closely watching the Federal Reserve’s next move, as speculation grows over potential rate hikes. The upcoming policy announcement is expected to influence investor confidence and overall market stability.
```

Output:
("entity"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"index"{tuple_delimiter}"The Global Tech Index tracks the performance of major technology stocks and experienced a 3.4% decline today."){record_delimiter}
("entity"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"company"{tuple_delimiter}"Nexon Technologies is a tech company that saw its stock decline by 7.8% after disappointing earnings."){record_delimiter}
("entity"{tuple_delimiter}"Omega Energy"{tuple_delimiter}"company"{tuple_delimiter}"Omega Energy is an energy company that gained 2.1% in stock value due to rising oil prices."){record_delimiter}
("entity"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"commodity"{tuple_delimiter}"Gold futures rose by 1.5%, indicating increased investor interest in safe-haven assets."){record_delimiter}
("entity"{tuple_delimiter}"Crude Oil"{tuple_delimiter}"commodity"{tuple_delimiter}"Crude oil prices rose to $87.60 per barrel due to supply constraints and strong demand."){record_delimiter}
("entity"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"market_trend"{tuple_delimiter}"Market selloff refers to the significant decline in stock values due to investor concerns over interest rates and regulations."){record_delimiter}
("entity"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"economic_policy"{tuple_delimiter}"The Federal Reserve's upcoming policy announcement is expected to impact investor confidence and market stability."){record_delimiter}
("relationship"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"The decline in the Global Tech Index is part of the broader market selloff driven by investor concerns."{tuple_delimiter}"market performance, investor sentiment"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Nexon Technologies' stock decline contributed to the overall drop in the Global Tech Index."{tuple_delimiter}"company impact, index movement"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"Gold prices rose as investors sought safe-haven assets during the market selloff."{tuple_delimiter}"market reaction, safe-haven investment"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"Speculation over Federal Reserve policy changes contributed to market volatility and investor selloff."{tuple_delimiter}"interest rate impact, financial regulation"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"market downturn, investor sentiment, commodities, Federal Reserve, stock performance"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: [economic_policy, athlete, event, location, record, organization, equipment]
Text:
```
At the World Athletics Championship in Tokyo, Noah Carter broke the 100m sprint record using cutting-edge carbon-fiber spikes.
```

Output:
("entity"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"event"{tuple_delimiter}"The World Athletics Championship is a global sports competition featuring top athletes in track and field."){record_delimiter}
("entity"{tuple_delimiter}"Tokyo"{tuple_delimiter}"location"{tuple_delimiter}"Tokyo is the host city of the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"athlete"{tuple_delimiter}"Noah Carter is a sprinter who set a new record in the 100m sprint at the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"record"{tuple_delimiter}"The 100m sprint record is a benchmark in athletics, recently broken by Noah Carter."){record_delimiter}
("entity"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"equipment"{tuple_delimiter}"Carbon-fiber spikes are advanced sprinting shoes that provide enhanced speed and traction."){record_delimiter}
("entity"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"organization"{tuple_delimiter}"The World Athletics Federation is the governing body overseeing the World Athletics Championship and record validations."){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"Tokyo"{tuple_delimiter}"The World Athletics Championship is being hosted in Tokyo."{tuple_delimiter}"event location, international competition"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"Noah Carter set a new 100m sprint record at the championship."{tuple_delimiter}"athlete achievement, record-breaking"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"Noah Carter used carbon-fiber spikes to enhance performance during the race."{tuple_delimiter}"athletic equipment, performance boost"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"The World Athletics Federation is responsible for validating and recognizing new sprint records."{tuple_delimiter}"sports regulation, record certification"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"athletics, sprinting, record-breaking, sports technology, competition"){completion_delimiter}
#############################""",
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS["entity_continue_extraction"] = """
MANY entities and relationships were missed in the last extraction.

---Remember Steps---

1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

---Output---

Add them below using the same format:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---'

It appears some entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["fail_response"] = (
    "Sorry, I'm not able to provide an answer to that question.[no-context]"
)

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to user query about Knowledge Base provided below.


---Goal---

Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. Do not include information not provided by Knowledge Base.

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Base---
{context_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- If you don't know the answer, just say so.
- Do not make anything up. Do not include information not provided by the Knowledge Base."""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query and conversation history.

---Goal---

Given the query and conversation history, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.

---Instructions---

- Consider both the current query and relevant conversation history when extracting keywords
- Output the keywords in JSON format, it will be parsed by a JSON parser, do not add any extra content in output
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes
  - "low_level_keywords" for specific entities or details

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Conversation History:
{history}

Current Query: {query}
######################
The `Output` should be human text, not unicode characters. Keep the same language as `Query`.
Output:

"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does international trade influence global economic stability?"
################
Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}
#############################""",
    """Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}
#############################""",
    """Example 3:

Query: "What is the role of education in reducing poverty?"
################
Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}
#############################""",
]


PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Document Chunks provided below.

---Goal---

Generate a concise response based on Document Chunks and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Document Chunks, and incorporating general knowledge relevant to the Document Chunks. Do not include information not provided by Document Chunks.

When handling content with timestamps:
1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content and the timestamp
3. Don't automatically prefer the most recent content - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Document Chunks---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- If you don't know the answer, just say so.
- Do not include information not provided by the Document Chunks."""


PROMPTS[
    "similarity_check"
] = """Please analyze the similarity between these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate whether these two questions are semantically similar, and whether the answer to Question 2 can be used to answer Question 1, provide a similarity score between 0 and 1 directly.

Similarity score criteria:
0: Completely unrelated or answer cannot be reused, including but not limited to:
   - The questions have different topics
   - The locations mentioned in the questions are different
   - The times mentioned in the questions are different
   - The specific individuals mentioned in the questions are different
   - The specific events mentioned in the questions are different
   - The background information in the questions is different
   - The key conditions in the questions are different
1: Identical and answer can be directly reused
0.5: Partially related and answer needs modification to be used
Return only a number between 0-1, without any additional content.
"""

PROMPTS["mix_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Data Sources provided below.


---Goal---

Generate a concise response based on Data Sources and follow Response Rules, considering both the conversation history and the current query. Data sources contain two parts: Knowledge Graph(KG) and Document Chunks(DC). Summarize all information in the provided Data Sources, and incorporating general knowledge relevant to the Data Sources. Do not include information not provided by Data Sources.

When handling information with timestamps:
1. Each piece of information (both relationships and content) has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content/relationship and the timestamp
3. Don't automatically prefer the most recent information - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Data Sources---

1. From Knowledge Graph(KG):
{kg_context}

2. From Document Chunks(DC):
{vector_context}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- Organize answer in sesctions focusing on one main point or aspect of the answer
- Use clear and descriptive section titles that reflect the content
- List up to 5 most important reference sources at the end under "References" sesction. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), in the following format: [KG/DC] Source content
- If you don't know the answer, just say so. Do not make anything up.
- Do not include information not provided by the Data Sources."""
