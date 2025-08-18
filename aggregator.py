import asyncio
from memory import Memory
from planning_engine import PlanningEngine
from llm_provider import OpenAIProvider
import json

from agents import Agent, ModelSettings, Runner
from agents.mcp import MCPServerStdio 

class AggregatorAgent:
    """Main aggregator agent that orchestrates the RAG process"""
    
    def __init__(self, flag_loop: bool = False):

        self.memory = Memory(short_term={}, long_term={})
        self.planning_engine = PlanningEngine()
        self.history = []
        self.current_agent = None
        self.llm_provider = OpenAIProvider()
        self._flag_queries_loop = flag_loop

        # Inicializar os agentes
        self._setup_agents()
    
    # def process_query(self, query: str) -> str:
    #     """Main method to process user query through agentic RAG pipeline"""
    #     pass

    def _setup_agents(self):
        """Configura todos os agentes"""
        self.agentRagEngineSource = Agent(
            name="RagEngineAssistant",
            model=self.llm_provider.model,
            handoff_description="Assistente para fazer buscas nas documentações locais RAG",
            instructions=
                "Você é um assistente para fazer buscas nas documentações oficiais que estão nas nossas bases locais." \
                "" \
                "Regras de uso: " \
                "- Identificar se o produto que está sendo questionado está nas nossas documentações, caso verdadeiro trazer o troubleshooting. " \
                "- Caso o cliente informar um produto que não se encontra na nossa documentaçao pedir para o SearchEngineAssistant fazer a busca." \
                "" \
                "Ferramenta: " \
                "- **get_info_support_apple**" \
                "",
            model_settings=ModelSettings(tool_choice="required", temperature=0, parallel_tool_calls=False), 
        )
        self.agentSearchEngineSource = Agent(
            name="SearchEngineAssistant",
            model=self.llm_provider.model,
            handoff_description="Assistente para fazer buscas de fontes externas na web",
            instructions=
                "Você DEVE usar a ferramenta search_web para todas as perguntas." \
                "SEMPRE execute search_web primeiro antes de responder." \
                "Se não conseguir usar search_web, explique o erro específico." \
                "" \
                "Processo obrigatório:" \
                "1. Recebeu pergunta → EXECUTE search_web" \
                "2. Aguarde resultado da busca" \
                "3. Responda baseado nos resultados" \
                "" \
                "Ferramenta:" \
                "- **search_web** - SEMPRE use esta ferramenta" \
                "",

            model_settings=ModelSettings(tool_choice="required", temperature=0, parallel_tool_calls=False), 
        )
        self.agentCloudEngineSource = Agent(
            name="CloudEngineAssistant",
            model=self.llm_provider.model,
            handoff_description="Assistente gestor do supporte.",
            instructions=
                "Você é o responsável pelas operações no sistema de ISTM do HelpDesk da Apple." \
                "Como administrador, você podera fazer buscas e persistencias. " \
                "" \
                "Você terá acesso as ferrramentas:" \
                "1. **search_tickets**: Consulta os tickets ou chamados" \
                "2. **search_knowledge_base**: Consulta a base de conhecimento" \
                "3. **get_customer_by_email**: Consulta as informações do usuário pelo email" \
                "4. **get_agent_workload**: Pega os agentes por workload" \
                "5. **create_ticket**: Cria um ticket novo ou abre um novo chamado" \
                "6. **update_ticket_status**: Atualiza o status do ticket ou chamado" \
                "7. **add_ticket_comment**: Adiciona um comentário no ticker ou chamado" \
                "8. **create_customer**: Cria um novo cliente na base" \
                "9. **create_kb_article**: Cria base de conhecimento" \
                "10. **increment_kb_view_count**: Fazer o incremento das visualizações na base de conhecimento" \
                "11. **get_ticket_statistics**: Pega as informações sobre as estatisticas dos chamados" \
                "" \
                "Regras para uso:" \
                "- Se precisar de informações técnicas para resolver tickets, " \
                "- COMUNIQUE-SE com RagEngineAssistant" \
                "- Você poderá fazer executar tudo o que o usuário lhe pedir."
                "" \
                "NUNCA use tools para:" \
                "- Conhecimento geral que você possui" \
                "- Perguntas conceituais básicas" \
                "- Conversas casuais" \
                "",
            model_settings=ModelSettings(tool_choice="required", temperature=0, parallel_tool_calls=False), 
        ) 
        self.agentAggregator = Agent(
            name="AggregatorAssistant",
            model=self.llm_provider.model,
            handoffs=[self.agentRagEngineSource, self.agentSearchEngineSource, self.agentCloudEngineSource],
            handoff_description="Orquestrador que direciona e EXECUTA as solicitações.",
            instructions="Você é responsável por analisar e EXECUTAR o handoff correto para cada tipo de pergunta." \
                "" \
                "REGRAS DE ROTEAMENTO (execute imediatamente):" \
                "" \
                "RagEngineAssistant para:" \
                "- Problemas técnicos e troubleshooting sobre produtos Apple (iPhone, Mac, iPad, Apple Watch, outros)" \
                #"- Informações sobre Apple em geral" \
                #"- Perguntas como: 'What do you know about Apple?', 'Apple products', 'Mac problems'" \
                "" \
                "SearchEngineAssistant para:" \
                "- Buscas de informações atuais na internet" \
                "- Notícias recentes" \
                "- Informações que não estão na documentação local" \
                "- Perguntas com: 'latest', 'current', 'recent', 'news'" \
                "" \
                "CloudEngineAssistant para:" \
                "- Operações com tickets/chamados" \
                "- Relatórios e estatísticas" \
                "- Gestão de clientes" \
                "- Perguntas com: 'ticket', 'report', 'customer', 'statistics'" \
                "" \
                "IMPORTANTE: EXECUTE o handoff imediatamente, não apenas informe.",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
        )

        # Define o agente inicial
        self.current_agent = self.agentAggregator

        if 1==0:
            """Configura todos os agentes"""
            self.agentRagEngineSource = Agent(
                name="RagEngineAssistant",
                model=self.llm_provider.model,
                handoff_description="Assistant for searching local RAG documentation",
                instructions="You will only answer the user's question. " \
                    "You are an assistant for searching official documentation found in our local databases. " \
                    "Identify whether the product being questioned is in our documentation. If so, bring up the troubleshooting. Use the tool (get_info_support_apple) " \
                    "If the customer reports a product that is not in our documentation, ask the SearchEngineAssistant to search for it. " \
                    "",
                model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
            )
            self.agentSearchEngineSource = Agent(
                name="SearchEngineAssistant",
                model=self.llm_provider.model,
                handoff_description="Assistant for searching external sources on the web",
                instructions="You will only answer the user's question. " \
                    "You are an assistant for performing internet searches that respect the context of the conversation and the user's request. " \
                    "All searches must be performed on reliable sources, always respecting the context of the request. " \
                    "The tool you will use to perform additional searches if necessary is called (search_web). " \
                    "",
                model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
            )
            self.agentCloudEngineSource = Agent(
                name="CloudEngineAssistant",
                model=self.llm_provider.model,
                handoff_description="Assistant Support Manager.",
                instructions="You will only answer the user's question. "\
                    "You are responsible for operations in the Apple HelpDesk ISTM system. " \
                    "As an administrator, you can perform searches and persistence. Using the tools described " \
                    "# Instructions for SEARCH UTILITY FUNCTIONS " \
                    "- To search tickets or calls, use the (search_tickets) tool " \
                    "- To search the knowledge base, use the (search_knowledge_base) tool " \
                    "- To search user information by email, use the (get_customer_by_email) tool " \
                    "- To get agents by workload, use the (get_agent_workload) tool " \
                    "# Instructions for PERSISTENCE UTILITY FUNCTIONS" \
                    "- To create a new ticket or open a new call, use the (create_ticket) tool. If the user doesn't provide the information, generate dummy information " \
                    "- To update the ticket or call status, use the (update_ticket_status) tool " \
                    "- To add a comment to a ticker or ticket, use the (add_ticket_comment) tool " \
                    "- To create a new customer in the database, use the (create_customer) tool " \
                    "- To create a knowledge base, use the (create_kb_article) tool" \
                    "- To increase the number of views in the knowledge base, use the (increment_kb_view_count) tool " \
                    "# Tools for REPORTING FUNCTIONS and STATISTICS " \
                    "- To get information about ticket statistics, use the (get_ticket_statistics) tool " \
                    "If you need technical information to resolve tickets, " \
                    "CONTACT RagEngineAssistant " \
                    "You can execute whatever the user asks you to. " \
                    "",
                model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
            ) 
            self.agentAggregator = Agent(
                name="AggregatorAssistant",
                model=self.llm_provider.model,
                handoffs=[self.agentRagEngineSource, self.agentSearchEngineSource, self.agentCloudEngineSource],
                instructions="You must understand the user's request and route to specialized agents. " \
                    #"You are responsible for reception and must ask in a friendly and polite manner what the user wants." \
                    #"When you route to another agent keep the question you received as input."
                    "You are responsible for orchestrating, receiving orders, and understanding requests to provide the best possible response. " \
                    "You must understand what the user is asking for and know how to route to the best agent. " \
                    "Use the following routing rules: " \
                    #"- You should prioritize searching in RagEngineAssintant"
                    "- Technical issues/troubleshooting → RagEngineAssistant " \
                    "- Web searches/external information to complement answers to questions → SearchEngineAssistant " \
                    "- Tickets/calls/customers/operations/reports/statistics ISTM → CloudEngineAssistant " \
                    "",
                model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
            )

            # Define o agente inicial
            self.current_agent = self.agentAggregator
    
    def reset_conversation(self):
        """Reseta completamente a conversa"""
        self.history = []


    async def _chat(self, query: str):
        """Processa a entrada do usuário e executa o chat"""
        # Adiciona a entrada do usuário ao histórico
        self.current_agent = self.agentAggregator
        
        self.history.append({
            "role": "user",
            "content": query
        })
        
        # Conecta com o servidor MCP e executa
        async with MCPServerStdio(params={"command": "mcp", "args": ["run", "mcp_base/server/server_support_apple.py"]}) as server:            
            # Atribui o servidor MCP aos agentes que precisam
            self.agentAggregator.mcp_servers = [server]
            self.agentRagEngineSource.mcp_servers = [server]
            self.agentSearchEngineSource.mcp_servers = [server] 
            self.agentCloudEngineSource.mcp_servers = [server]

            try:
                # Executa o runner
                result = await Runner.run(
                    starting_agent=self.current_agent, 
                    input=self.history, 
                    context=self.history
                )
                
                # Atualiza o estado
                self.current_agent = result.last_agent
                self.history = result.to_input_list()
                return result
                
            except Exception as e:
                print(f"ERRO no Runner: {e}")
                import traceback
                traceback.print_exc()
                return None

    def process_query(self, query: str) -> str:
        print(f"📥 Processing query: {query}")
        
        if self._flag_queries_loop:
            self.reset_conversation()
        
        # Step 1: Planning Phase
        print("🧠 Planning Phase...")
        memory_context = self.memory.get_relevant_context(query)

        plan = self.planning_engine.create_plan(query, memory_context)
        
        print(f"   Plan created with {len(plan.steps)} steps")
        
        # Step 2: Information Retrieval Phase
        print("🔍 Fetching Phase...")
        retrieved_context = {}
        
        source_data = asyncio.run(self._chat(query=query))
        retrieved_context["local"] = { 
            "source" : self.current_agent.name,
            "results": source_data.final_output 
        }
        plan.data_sources=retrieved_context["local"]["source"]
        print(f"   Data sources: {plan.data_sources}")
        
        # Step 3: Context Enhancement
        print("🔧 Context Enhancement...")
        enhanced_context = {
            "memory_context": memory_context,
            "retrieved_context": retrieved_context,
            "reasoning_trace": plan.reasoning_trace,
            "query": query
        }
        
        # Step 4: Generation Phase
        print("✨ Generation Phase...")
        context_str = json.dumps(enhanced_context, indent=2)
        response = self.llm_provider.generate(query, context_str)
        
        # Step 5: Memory Update
        print("💾 Memory Update...")
        self.memory.add_short_term(f"query_{len(self.memory.short_term)}", {
            "query": query,
            "response": response,
            "context": enhanced_context
        })
        
        print("✅ Process complete!")

        return response
