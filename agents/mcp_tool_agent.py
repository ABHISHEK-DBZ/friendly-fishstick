"""
MCP Tool Integration - GitHub Models MCP Tools
Demonstrates: MCP (Model Context Protocol) Tool Usage
"""
import logging
import json
from typing import Dict, Any, List
from agent_framework import BaseAgent, handler

logger = logging.getLogger(__name__)


class MCPToolAgent(BaseAgent):
    """
    Agent that uses MCP (Model Context Protocol) tools for enhanced capabilities.
    
    MCP Tools Demonstrated:
    1. External API calls via MCP
    2. Tool chaining
    3. Context-aware tool selection
    """
    
    def __init__(self, chat_client):
        super().__init__(name="MCPTool")
        self.chat_client = chat_client
        logger.info("MCP Tool Agent initialized")
        
        # Define available MCP tools
        self.mcp_tools = self._define_mcp_tools()
    
    def _define_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Define MCP tools available to the agent.
        
        These tools follow the Model Context Protocol specification.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_agricultural_database",
                    "description": "Search a database of agricultural research papers and case studies",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for agricultural information"
                            },
                            "filters": {
                                "type": "object",
                                "properties": {
                                    "region": {"type": "string"},
                                    "crop_type": {"type": "string"},
                                    "disease": {"type": "string"}
                                }
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_prices",
                    "description": "Get current market prices for crops and agricultural products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "crop": {
                                "type": "string",
                                "description": "Name of the crop"
                            },
                            "location": {
                                "type": "string",
                                "description": "Market location"
                            }
                        },
                        "required": ["crop"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_pesticide_safety",
                    "description": "Check safety information and regulations for pesticides",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pesticide_name": {
                                "type": "string",
                                "description": "Name of the pesticide"
                            },
                            "crop": {
                                "type": "string",
                                "description": "Crop it will be used on"
                            }
                        },
                        "required": ["pesticide_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_government_schemes",
                    "description": "Get information about government agricultural schemes and subsidies",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "state": {
                                "type": "string",
                                "description": "Indian state"
                            },
                            "scheme_type": {
                                "type": "string",
                                "description": "Type of scheme (subsidy, insurance, loan, etc.)"
                            }
                        },
                        "required": ["state"]
                    }
                }
            }
        ]
    
    async def use_mcp_tools(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use MCP tools to enhance diagnosis with external data.
        """
        logger.info("MCP Tool Agent: Starting tool usage")
        
        diagnosis = state.get("diagnosis_summary", "")
        location = state.get("location", "India")
        
        try:
            # Prepare prompt with tool definitions
            tool_usage_prompt = f"""
Based on this plant diagnosis, determine which MCP tools would be helpful:

**Diagnosis**: {diagnosis}
**Location**: {location}

**Available MCP Tools**:
{json.dumps(self.mcp_tools, indent=2)}

Analyze the diagnosis and suggest:
1. Which tools should be called
2. What parameters to use
3. How the tool results would help the farmer

Format as JSON with keys: recommended_tools (array), reasoning, expected_benefits
"""
            
            messages = [{"role": "user", "content": tool_usage_prompt}]
            response = await self.chat_client.complete(messages=messages)
            
            tool_recommendations = response.choices[0].message.content
            
            # Simulate tool calls (in real implementation, these would call actual APIs)
            tool_results = await self._simulate_tool_calls(tool_recommendations, state)
            
            logger.info(f"MCP tools executed: {len(tool_results)} results")
            
            return {
                "tool_recommendations": tool_recommendations,
                "tool_results": tool_results
            }
        
        except Exception as e:
            logger.error(f"MCP tool usage failed: {str(e)}")
            return {"error": str(e)}
    
    async def _simulate_tool_calls(self, recommendations: str, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulate MCP tool calls.
        In production, these would call actual APIs via MCP.
        """
        results = []
        
        try:
            rec_json = json.loads(recommendations)
            recommended_tools = rec_json.get("recommended_tools", [])
            
            for tool in recommended_tools:
                tool_name = tool.get("name")
                
                if tool_name == "search_agricultural_database":
                    results.append({
                        "tool": tool_name,
                        "result": {
                            "papers_found": 15,
                            "top_result": "Integrated Management of Tomato Early Blight in Indian Conditions",
                            "success_rate": "85% with recommended treatment"
                        }
                    })
                
                elif tool_name == "get_market_prices":
                    results.append({
                        "tool": tool_name,
                        "result": {
                            "crop": tool.get("parameters", {}).get("crop", "tomato"),
                            "price_per_kg": "₹25-30",
                            "trend": "Stable",
                            "market": state.get("location", "India")
                        }
                    })
                
                elif tool_name == "check_pesticide_safety":
                    results.append({
                        "tool": tool_name,
                        "result": {
                            "pesticide": tool.get("parameters", {}).get("pesticide_name"),
                            "safety_rating": "Approved for use",
                            "waiting_period": "7 days before harvest",
                            "precautions": ["Use protective equipment", "Avoid during flowering"]
                        }
                    })
                
                elif tool_name == "get_government_schemes":
                    results.append({
                        "tool": tool_name,
                        "result": {
                            "schemes": [
                                {
                                    "name": "Pradhan Mantri Fasal Bima Yojana",
                                    "type": "Crop Insurance",
                                    "coverage": "Up to 100% of sum insured"
                                },
                                {
                                    "name": "Kisan Credit Card",
                                    "type": "Credit",
                                    "benefit": "Low interest agricultural loans"
                                }
                            ]
                        }
                    })
        
        except Exception as e:
            logger.error(f"Tool simulation failed: {str(e)}")
            results.append({"error": str(e)})
        
        return results
    
    @handler
    async def handle_mcp_tools(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool usage."""
        logger.info("MCP Tool Agent: Running")
        
        mcp_results = await self.use_mcp_tools(state)
        
        # Add MCP results to state
        state["mcp_tool_results"] = mcp_results
        
        logger.info("MCP Tool Agent: Completed")
        return state
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        return self.mcp_tools
