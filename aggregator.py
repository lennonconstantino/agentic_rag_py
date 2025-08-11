import asyncio
from memory import Memory
from planning_engine import PlanningEngine
from datasource import LocalDataSource, SearchEngineSource, CloudEngineSource
from llm_provider import OpenAIProvider
import json

from agents import Agent, ModelSettings, Runner
from agents.mcp import MCPServerStdio 

class AggregatorAgent:
    """Main aggregator agent that orchestrates the RAG process"""
    
    def __init__(self):
        self.memory = Memory(short_term={}, long_term={})
        self.planning_engine = PlanningEngine()
        # self.data_sources = {
        #     "local": LocalDataSource({"ai": "starting"}),
        #     "search_engine": SearchEngineSource(),
        #     "cloud_engine": CloudEngineSource()
        # }
        self.history = []
        self.current_agent = None
        self.llm_provider = OpenAIProvider()

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
            instructions="Você só vai responder a pergunta do usuário." \
                "Você é um assistente para fazer buscas nas documentações oficiais que estão nas nossas bases locais" \
                "Identifique se o produto que está sendo questionado está nas nossas documentações, caso verdadeiro trazer o troubleshooting. Usar a ferramenta (get_info_support_apple)" \
                "Caso o cliente informar um produto que não se encontra na nossa documentaçao pedir para o SearchEngineAssistant fazer a busca",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
        )
        self.agentSearchEngineSource = Agent(
            name="SearchEngineAssistant",
            model=self.llm_provider.model,
            handoff_description="Assistente para fazer buscas de fontes externas na web",
            instructions="Você só vai responder a pergunta do usuário." \
                "Você é um assistente para fazer buscas na internet que obdeçam o contexto da conversa e solicitaçao do usuário." \
                "Todas as buscas devem ser feitas em fontes confiáveis sempre respeitando o contexto da solicitação" \
                "A ferramenta que você vai usar para fazer as buscas complementares caso necessário se chama (search_web)",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
        )
        self.agentCloudEngineSource = Agent(
            name="CloudEngineAssistant",
            model=self.llm_provider.model,
            handoff_description="Assistente que fará a gestão do supporte.",
            instructions="Você só vai responder a pergunta do usuário."\
                "Você é o responsável pelas operações no sistema de ISTM do HelpDesk da Apple." \
                "Como administrador, você podera fazer buscas e persistencias. Através das Ferramentas descritas" \
                "# Instruçoes para FUNÇÕES DE UTILITÁRIO DE PESQUISA" \
                "- Para consultar os tickets ou chamados, use a ferramenta (search_tickets)" \
                "- Para consultar a base de conhecimento, use a ferramenta (search_knowledge_base)" \
                "- Para consultar as informações do usuário pelo email, use a ferramenta (get_customer_by_email)" \
                "- Para pegar os agentes por workload, use a ferramenta (get_agent_workload)" \
                "# Instruções para FUNÇÕES UTILITÁRIAS DE PERSISTÊNCIA" \
                "- Para criar um ticket novo ou abre um novo chamado, use a ferramenta (create_ticket), se o usuario nao te passar as informações gere informações ficticias" \
                "- Para atualizar o status do ticket ou chamado, use a ferramenta (update_ticket_status)" \
                "- Para adicionar um comentário no ticker ou chamado, use a ferramenta (add_ticket_comment)" \
                "- Para criar um novo cliente na base, use a ferramenta (create_customer)" \
                "- Para criar base de conhecimento use a ferramenta (create_kb_article)" \
                "- Para fazer o incremento de visualizações da base de conhecimento, use a ferramenta (increment_kb_view_count)" \
                "# Ferramentas para FUNÇÕES DE RELATÓRIOS e ESTATÍSTICAS" \
                "- Para pegar as informações sobre as estatisticas dos chamados, use a ferramenta (get_ticket_statistics)" \
                "Se precisar de informações técnicas para resolver tickets, " \
                "COMUNIQUE-SE com RagEngineAssistant" \
                "Você poderá fazer executar tudo o que o usuário lhe pedir."
                "",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
        ) 
        self.agentAggregator = Agent(
            name="AggregatorAssistant",
            model=self.llm_provider.model,
            handoffs=[self.agentRagEngineSource, self.agentSearchEngineSource, self.agentCloudEngineSource],
            instructions="Você só vai entender qual é a solicitação e rotear das solicitações dos usuários." \
                #"Você é responsável pela recepção e deve perguntar de maneira cordial e educada o que o usuário deseja. " \
                #"Quando você rotear a para outro agente manter a pergunta que você recebeu como entrada."
                "Você é responsável por orquestrar, receber os pedidos e entender as solicitações para dar a melhor resposta possível. " \
                "Você deve entender o que o usuário está pedindo e saber rotear para o melhor agente. " \
                "Use as seguintes regras de roteamento: " \
                #"- Você deve priorizar a busca no RagEngineAssintant"
                "- Problemas técnicos/troubleshooting → RagEngineAssistant " \
                "- Buscas na web/informações externas para complementação de resposta para as perguntas → SearchEngineAssistant " \
                "- Tickets/chamados/clientes/operações/relatórios/estatíscas ISTM → CloudEngineAssistant " \
                "",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
        )

        # Define o agente inicial
        self.current_agent = self.agentAggregator
    
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
            self.agentRagEngineSource.mcp_servers = [server]
            self.agentSearchEngineSource.mcp_servers = [server] 
            self.agentCloudEngineSource.mcp_servers = [server]
            
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

    def process_query(self, query: str) -> str:
        print(f"📥 Processing query: {query}")
        
        # Step 1: Planning Phase
        print("🧠 Planning Phase...")
        memory_context = self.memory.get_relevant_context(query)

        # TODO... ver qual é o tipo da query

        plan = self.planning_engine.create_plan(query, memory_context)
        
        print(f"   Plan created with {len(plan.steps)} steps")
        print(f"   Data sources: {plan.data_sources}")
        
        # Step 2: Information Retrieval Phase
        print("🔍 Fetching Phase...")
        retrieved_context = {}
        
        # for source_name in plan.data_sources:
        #     if source_name in self.data_sources:
        #         source_data = self.data_sources[source_name].fetch(query)
        #         retrieved_context[source_name] = source_data
        #         print(f"   ✓ Fetched from {source_name}")

        source_data = asyncio.run(self._chat(query=query))
        retrieved_context["local"] = { 
            "source" : self.current_agent.name,
            "results": source_data.final_output 
        }
        print("::: ", retrieved_context["local"]["source"])
        
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
        # print("="*60)
        # print(context_str)
        # print("="*60)
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
