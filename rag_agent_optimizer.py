"""
RAG Agent Optimizer: Query Recognition & Routing System
Intelligently routes queries to appropriate knowledge domains and provides
optimized prompts for semantic search and retrieval.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# DOMAIN TAXONOMY & RECOGNITION
# ============================================================================

class KnowledgeDomain(Enum):
    """Enumeration of knowledge domains in the RAG system"""
    DESIGN_GRAPHICS = "design_graphics"
    DTF_PRINTING = "dtf_printing"
    BUSINESS_AUTOMATION = "business_automation"
    LEGAL_COMPLIANCE = "legal_compliance"
    SAAS_SOFTWARE_LAW = "saas_software_law"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    FUNDRAISING_VC = "fundraising_vc"
    ECOMMERCE = "ecommerce"
    GENERAL = "general"


@dataclass
class DomainMetadata:
    """Metadata for each knowledge domain"""
    domain: KnowledgeDomain
    keywords: List[str]
    sources: List[str]
    topics: List[str]
    description: str
    triggers: List[str]


# Domain definitions with comprehensive metadata
DOMAIN_REGISTRY: Dict[KnowledgeDomain, DomainMetadata] = {

    KnowledgeDomain.DESIGN_GRAPHICS: DomainMetadata(
        domain=KnowledgeDomain.DESIGN_GRAPHICS,
        keywords=[
            "design", "graphics", "figma", "gimp", "inkscape", "svg", "canvas",
            "ui", "ux", "visual", "icon", "typography", "font", "color", "layout",
            "imagemagick", "pillow", "cairo", "pdf", "vector", "raster"
        ],
        sources=[
            "Figma API Docs", "GIMP Docs", "Inkscape Docs", "ImageMagick Docs",
            "Pillow Docs", "Cairo Docs", "SVG Specification", "Canvas API",
            "Typography Guidelines", "Design Systems Documentation"
        ],
        topics=[
            "Vector graphics design and editing",
            "Raster image processing and manipulation",
            "Web design and UI/UX frameworks",
            "Typography and font systems",
            "Design system implementation",
            "SVG and vector formats",
            "PDF generation and manipulation",
            "Color management and theory",
            "Design-to-code workflows"
        ],
        description="Visual design, graphics processing, and design tools",
        triggers=[
            "How do I design a UI component?",
            "I need to edit vector graphics",
            "How do I generate PDFs programmatically?",
            "What's the best way to handle SVG in web apps?",
            "I need to process images programmatically",
            "How do I build a design system?",
            "I need to generate graphics from data"
        ]
    ),

    KnowledgeDomain.DTF_PRINTING: DomainMetadata(
        domain=KnowledgeDomain.DTF_PRINTING,
        keywords=[
            "dtf", "direct-to-film", "heat", "press", "ink", "white ink",
            "film", "powder", "garment", "t-shirt", "rip", "color separation",
            "halftone", "screen", "temperature", "safety", "osha", "equipment"
        ],
        sources=[
            "DTF Printing Guide", "Heat Press Safety Standards", "OSHA Guidelines",
            "Film Specification Sheets", "White Ink Chemistry Documentation",
            "RIP Software Documentation", "Profitability Analysis Guides"
        ],
        topics=[
            "DTF printing process and workflow",
            "Heat press operation and safety",
            "Film and white ink chemistry",
            "RIP software configuration",
            "Color separation and halftoning",
            "Equipment maintenance and troubleshooting",
            "Cost analysis and profitability",
            "Garment preparation and handling",
            "Temperature and timing specifications"
        ],
        description="Direct-to-film printing, equipment, chemistry, and operations",
        triggers=[
            "What's the right temperature for DTF heat press?",
            "How do I set up white ink in my RIP software?",
            "What are the safety precautions for heat press operation?",
            "How do I calculate profitability for DTF printing?",
            "What film specifications should I use?",
            "How do I troubleshoot color separation issues?",
            "I need cost analysis for DTF equipment"
        ]
    ),

    KnowledgeDomain.BUSINESS_AUTOMATION: DomainMetadata(
        domain=KnowledgeDomain.BUSINESS_AUTOMATION,
        keywords=[
            "automation", "workflow", "email", "automation platform", "scheduler",
            "trigger", "action", "integration", "api", "webhook", "n8n",
            "airflow", "temporal", "prefect", "accounting", "erp", "odoo",
            "invoice", "ledger", "postal", "nodemailer", "mautic"
        ],
        sources=[
            "n8n Documentation", "Apache Airflow Docs", "Temporal Docs", "Prefect Docs",
            "ERPNext Documentation", "Odoo Documentation", "Akaunting Docs",
            "Invoice Ninja Docs", "Postal Email Service", "Nodemailer Docs",
            "Mautic Marketing Automation"
        ],
        topics=[
            "Workflow automation and orchestration",
            "Email automation and sending",
            "Business process automation",
            "Accounting and ERP systems",
            "Invoice and ledger management",
            "Webhook and API integrations",
            "Scheduled tasks and cron jobs",
            "Data transformation pipelines",
            "Marketing automation workflows"
        ],
        description="Business process automation, workflows, accounting, and integration",
        triggers=[
            "How do I automate email sending?",
            "I need to build a workflow automation system",
            "How do I integrate multiple business tools?",
            "What's the best way to handle invoicing?",
            "How do I set up scheduled tasks?",
            "I need accounting system integration",
            "How do I automate business processes?",
            "I need marketing automation capabilities"
        ]
    ),

    KnowledgeDomain.LEGAL_COMPLIANCE: DomainMetadata(
        domain=KnowledgeDomain.LEGAL_COMPLIANCE,
        keywords=[
            "legal", "compliance", "law", "contract", "formation", "business",
            "registration", "florida", "orlando", "gdpr", "privacy", "oss",
            "license", "trademark", "copyright", "terms", "agreement"
        ],
        sources=[
            "Florida Department of State", "Florida Bar Association",
            "Orlando Business Resources", "ContractWorks", "LegalZoom",
            "GDPR Documentation", "Open Source License Database",
            "DocAssemble Legal Document Automation"
        ],
        topics=[
            "Business formation and registration",
            "Florida-specific business law",
            "Orlando regional compliance",
            "Contract templates and automation",
            "GDPR and privacy compliance",
            "Open source license compliance",
            "Terms of service drafting",
            "Business legal requirements",
            "Document automation for legal"
        ],
        description="Business law, compliance, contracts, and legal documentation",
        triggers=[
            "How do I form an LLC in Florida?",
            "What are the compliance requirements in Orlando?",
            "How do I automate contract generation?",
            "I need GDPR compliance guidance",
            "What open source licenses should I use?",
            "I need to draft terms of service",
            "What are the legal requirements for my business?"
        ]
    ),

    KnowledgeDomain.SAAS_SOFTWARE_LAW: DomainMetadata(
        domain=KnowledgeDomain.SAAS_SOFTWARE_LAW,
        keywords=[
            "saas", "software", "law", "multi-tenant", "licensing", "terms",
            "tos", "eula", "subscription", "compliance", "data handling",
            "user data", "agreement", "liability", "warranty"
        ],
        sources=[
            "SaaS Legal & Compliance Framework",
            "Software IP Law Resources",
            "Multi-Tenant Architecture Legal Issues",
            "SaaS Terms of Service Guidelines"
        ],
        topics=[
            "SaaS business model legal considerations",
            "Multi-tenant architecture legal issues",
            "SaaS terms of service best practices",
            "Subscription licensing models",
            "Data handling and compliance",
            "User agreement drafting",
            "Liability and warranty considerations",
            "Compliance with data regulations"
        ],
        description="SaaS legal frameworks, software law, and licensing",
        triggers=[
            "What legal issues should I consider for SaaS?",
            "How do I structure a SaaS terms of service?",
            "What are the legal implications of multi-tenant architecture?",
            "I need SaaS licensing best practices",
            "How do I handle user data legally in SaaS?"
        ]
    ),

    KnowledgeDomain.INTELLECTUAL_PROPERTY: DomainMetadata(
        domain=KnowledgeDomain.INTELLECTUAL_PROPERTY,
        keywords=[
            "patent", "ip", "intellectual property", "trademark", "copyright",
            "patent search", "patent filing", "software patent", "invention",
            "protectable", "disclosure", "claims", "prior art", "patent office"
        ],
        sources=[
            "USPTO Patents Database", "Patent Search Documentation",
            "Software IP Law Resources", "Patent Filing Procedures",
            "Intellectual Property Guides"
        ],
        topics=[
            "Patent search and prior art research",
            "Patent filing procedures",
            "Software patent protection",
            "Trademark registration and protection",
            "Copyright and licensing",
            "Trade secret protection",
            "IP strategy and planning",
            "Patent prosecution and maintenance"
        ],
        description="Intellectual property, patents, trademarks, and copyrights",
        triggers=[
            "How do I search for existing patents?",
            "What's the process for filing a patent?",
            "How do I protect my software with a patent?",
            "Should I trademark my product name?",
            "What copyright protection do I get automatically?",
            "I need to research prior art for my invention"
        ]
    ),

    KnowledgeDomain.FUNDRAISING_VC: DomainMetadata(
        domain=KnowledgeDomain.FUNDRAISING_VC,
        keywords=[
            "fundraising", "funding", "venture capital", "vc", "grant", "sba",
            "startup", "investor", "pitch", "equity", "cap table", "valuation",
            "due diligence", "term sheet", "y combinator", "ycombinator",
            "federal grants", "small business", "loans", "venture"
        ],
        sources=[
            "Y Combinator Startup Library", "Paul Graham VC Essays",
            "Federal Grants (Grants.gov)", "SBA Funding Resources",
            "Equity & Cap Table Management Tools",
            "Venture Capital Resources"
        ],
        topics=[
            "Startup funding sources and strategies",
            "Venture capital process and due diligence",
            "Federal grant opportunities",
            "SBA loans and small business funding",
            "Equity and cap table management",
            "Pitch preparation and investor relations",
            "Valuation and term sheets",
            "Founder resources and playbooks",
            "VC due diligence preparation"
        ],
        description="Fundraising, venture capital, grants, and startup funding",
        triggers=[
            "What are my options for startup funding?",
            "How do I prepare for a venture capital pitch?",
            "What federal grants are available for my business?",
            "I need to manage my cap table",
            "How do I value my startup?",
            "What's the process for raising venture capital?",
            "I need SBA loan information",
            "How do I structure equity for my startup?"
        ]
    ),

    KnowledgeDomain.ECOMMERCE: DomainMetadata(
        domain=KnowledgeDomain.ECOMMERCE,
        keywords=[
            "ecommerce", "e-commerce", "shop", "store", "product", "cart",
            "checkout", "payment", "shopify", "woocommerce", "magento",
            "prestashop", "opencart", "medusa", "saleor", "headless",
            "commerce", "order", "inventory", "catalog"
        ],
        sources=[
            "Shopify Commerce Platform", "WooCommerce", "Magento",
            "PrestaShop", "OpenCart", "Medusa Headless Commerce",
            "Saleor GraphQL Commerce", "Vue Storefront PWA",
            "Sylius Symfony Commerce", "Bagisto Laravel Ecommerce",
            "Webiny Serverless Commerce"
        ],
        topics=[
            "Ecommerce platform selection and implementation",
            "Product catalog and inventory management",
            "Shopping cart and checkout flows",
            "Payment gateway integration",
            "Order management systems",
            "Headless commerce architecture",
            "API-first ecommerce development",
            "Multi-channel selling strategies",
            "Ecommerce performance optimization",
            "PWA and progressive commerce"
        ],
        description="E-commerce platforms, architecture, and implementation",
        triggers=[
            "Which ecommerce platform should I use?",
            "How do I set up a headless commerce solution?",
            "I need to integrate payment gateways",
            "How do I build a PWA for ecommerce?",
            "I need multi-channel selling capabilities",
            "How do I optimize ecommerce performance?",
            "I need GraphQL-based ecommerce",
            "How do I manage a large product catalog?"
        ]
    ),

    KnowledgeDomain.GENERAL: DomainMetadata(
        domain=KnowledgeDomain.GENERAL,
        keywords=[],
        sources=["Cross-Domain Knowledge"],
        topics=["General questions", "Cross-domain queries"],
        description="General knowledge across all domains",
        triggers=[]
    )
}


# ============================================================================
# RECOGNITION FUNCTION
# ============================================================================

class QueryRecognizer:
    """Intelligent query recognition and domain routing"""

    def __init__(self, domain_registry: Dict[KnowledgeDomain, DomainMetadata] = DOMAIN_REGISTRY):
        self.registry = domain_registry
        self._build_keyword_index()

    def _build_keyword_index(self):
        """Build inverted index of keywords to domains for fast lookup"""
        self.keyword_index = {}
        for domain, metadata in self.registry.items():
            for keyword in metadata.keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append(domain)

    def recognize(self, query: str) -> Tuple[KnowledgeDomain, float, List[str]]:
        """
        Recognize the primary domain and confidence of a query

        Returns:
            Tuple of (primary_domain, confidence_score, matched_keywords)
        """
        query_lower = query.lower()
        domain_scores = {}
        matched_keywords = []

        # Score domains based on keyword matches
        for keyword, domains in self.keyword_index.items():
            if keyword in query_lower:
                matched_keywords.append(keyword)
                for domain in domains:
                    domain_scores[domain] = domain_scores.get(domain, 0) + 1

        # If no keywords matched, return GENERAL
        if not domain_scores:
            return KnowledgeDomain.GENERAL, 0.0, []

        # Get top domain
        primary_domain = max(domain_scores, key=domain_scores.get)
        confidence = min(domain_scores[primary_domain] / len(query_lower.split()), 1.0)

        return primary_domain, confidence, matched_keywords

    def get_domain_context(self, domain: KnowledgeDomain) -> DomainMetadata:
        """Get metadata for a specific domain"""
        return self.registry.get(domain, self.registry[KnowledgeDomain.GENERAL])


# ============================================================================
# RAG AGENT SYSTEM PROMPTS
# ============================================================================

class RAGAgentPrompts:
    """System prompts for RAG agent operation"""

    @staticmethod
    def SYSTEM_PROMPT_DEFINITION() -> str:
        """
        PRIMARY SYSTEM PROMPT: Defines what the RAG Agent is and its core function

        Use this as the base system prompt for the RAG knowledge retrieval agent
        """
        return """You are the RAG Knowledge Retrieval Agent - an expert system designed to provide
accurate, fact-based technical documentation and code examples from a comprehensive
knowledge base containing 600,000+ chunks across 200+ sources.

YOUR PRIMARY FUNCTION:
You are a specialized AI assistant that acts as an intelligent knowledge retrieval
interface. Your role is to:
1. Understand user queries about technical topics
2. Recognize the knowledge domain (design, DTF, business automation, legal, SaaS law, IP, fundraising, ecommerce)
3. Retrieve relevant documentation and examples from the appropriate knowledge sources
4. Present information with proper citations and source attribution
5. Provide actionable, accurate technical guidance

YOUR KNOWLEDGE DOMAINS (with 50+ sources):
- Design & Graphics (13 sources): Figma, GIMP, Inkscape, SVG, PDF, Canvas, Typography
- DTF Printing & Business (23 sources): Heat press, RIP software, workflow automation, accounting
- Legal & Compliance (16 sources): Florida law, SaaS law, patents, GDPR, contracts, grants
- E-Commerce (10 sources): Shopify, WooCommerce, Magento, Medusa, Saleor, Vue Storefront, Webiny

YOUR CONSTRAINTS & PRINCIPLES:
- Always provide citations and source attribution when retrieving from knowledge base
- Admit when information is not in your knowledge base
- Prioritize accuracy over completeness
- Include relevant code examples when available
- Explain technical concepts clearly for the target audience
- Flag if a query spans multiple knowledge domains

QUERY HANDLING FLOW:
1. Parse the user query to identify the knowledge domain
2. Extract key technical terms and context
3. Query the RAG knowledge base with domain-specific filters
4. Retrieve relevant documentation chunks with highest semantic similarity
5. Synthesize information with proper source attribution
6. Provide actionable recommendations based on retrieved knowledge

SUCCESS METRIC:
You succeed when users get accurate, well-sourced technical information that directly
answers their question without requiring external searches."""

    @staticmethod
    def OPERATION_PROMPT_ROUTING() -> str:
        """
        SECONDARY OPERATION PROMPT: Defines when/how to use the RAG agent and routing logic

        Use this prompt to determine if/when to invoke the RAG knowledge system and how to handle results
        """
        return """WHEN TO INVOKE RAG KNOWLEDGE RETRIEVAL:

TRIGGER CONDITIONS (Activate RAG Agent):
✓ Questions about specific technologies, frameworks, or tools in knowledge base
✓ How-to questions requiring technical documentation or code examples
✓ Comparative questions about multiple platforms/approaches
✓ Troubleshooting questions about known software/systems
✓ Questions about business processes, compliance, or legal frameworks
✓ Ecommerce architecture and platform selection questions
✓ DTF printing operations, equipment, or business questions
✓ Design tools and graphics programming questions
✓ Startup funding, grants, or venture capital questions
✓ SaaS architecture, licensing, or legal questions

SKIP RAG RETRIEVAL FOR:
✗ Generic questions not related to technical documentation
✗ Personal advice or subjective preferences
✗ Current events or real-time information
✗ Requests for original creation (unless asking for code patterns from docs)
✗ Questions clearly outside documented knowledge domains

DOMAIN ROUTING RULES:

[Design & Graphics Queries]
Keywords: design, graphics, figma, gimp, inkscape, svg, canvas, ui, ux, visual, icon, pdf, vector, raster
Sources: Figma, GIMP, Inkscape, ImageMagick, Pillow, Cairo, SVG, Canvas API, Typography, Design Systems
Example Triggers:
- "How do I design a responsive UI?"
- "I need to generate PDFs programmatically"
- "What's the best way to handle SVG in web apps?"

[DTF Printing & Business Automation]
Keywords: dtf, heat, press, workflow, automation, email, accounting, erp, odoo, n8n, airflow
Sources: DTF Guides, Heat Press Safety, RIP Software, n8n, Airflow, Temporal, ERPNext, Odoo
Example Triggers:
- "What's the right temperature for DTF heat press?"
- "How do I automate business processes?"
- "How do I set up workflow automation?"

[Legal, Compliance & IP]
Keywords: legal, compliance, florida, business, registration, contract, gdpr, patent, oss, license
Sources: Florida DOS, Florida Bar, ContractWorks, LegalZoom, USPTO, GDPR, OSS Licenses
Example Triggers:
- "How do I form an LLC in Florida?"
- "What open source licenses should I use?"
- "How do I file a patent?"

[SaaS & Software Law]
Keywords: saas, multi-tenant, terms of service, licensing, subscription, software law, data compliance
Sources: SaaS Legal Frameworks, Software IP Law, Multi-Tenant Architecture, Terms Guidelines
Example Triggers:
- "What legal issues should I consider for SaaS?"
- "How do I structure a SaaS terms of service?"

[Fundraising & Venture Capital]
Keywords: fundraising, funding, venture capital, vc, grant, sba, startup, equity, cap table, pitch
Sources: Y Combinator, Paul Graham, Grants.gov, SBA, Cap Table Tools
Example Triggers:
- "What are my options for startup funding?"
- "How do I prepare for a VC pitch?"
- "What federal grants are available?"

[E-Commerce Platforms]
Keywords: ecommerce, shop, store, shopify, woocommerce, magento, headless, commerce, product, checkout
Sources: Shopify, WooCommerce, Magento, Medusa, Saleor, Vue Storefront, Webiny
Example Triggers:
- "Which ecommerce platform should I use?"
- "How do I set up a headless commerce solution?"
- "I need GraphQL-based ecommerce"

OUTPUT FORMAT FOR RAG RESPONSES:
1. DOMAIN IDENTIFICATION: State which knowledge domain the query belongs to
2. RETRIEVED KNOWLEDGE: Present relevant documentation chunks with source attribution
3. SYNTHESIS: Explain how the retrieved information answers the query
4. RECOMMENDATIONS: Provide actionable next steps based on retrieved knowledge
5. SOURCE CITATIONS: Link back to original documentation source

CONFIDENCE THRESHOLDS:
- High Confidence (>0.7): Retrieved information directly answers the query
- Medium Confidence (0.4-0.7): Retrieved information is relevant but may need supplementation
- Low Confidence (<0.4): Limited relevant information found; may need broader search or clarification

ERROR HANDLING:
- If no relevant sources found: "Your query doesn't match available knowledge domains. Consider reformulating or checking if this topic is covered."
- If query spans multiple domains: "Your question spans multiple knowledge domains. I'll retrieve information from [Domain1] and [Domain2]."
- If incomplete match: "I found partial matches in [Domain]. Additional context would help refine the search."""


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Initialize recognizer
    recognizer = QueryRecognizer()

    # Example queries
    test_queries = [
        "How do I design a responsive UI component?",
        "What's the right temperature for DTF heat press?",
        "How do I form an LLC in Florida?",
        "What ecommerce platform should I use?",
        "How do I get venture capital funding?",
        "How do I file a software patent?"
    ]

    print("=" * 80)
    print("RAG AGENT RECOGNITION & ROUTING SYSTEM")
    print("=" * 80)

    for query in test_queries:
        domain, confidence, keywords = recognizer.recognize(query)
        metadata = recognizer.get_domain_context(domain)

        print(f"\nQuery: {query}")
        print(f"Domain: {domain.value}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Matched Keywords: {', '.join(keywords)}")
        print(f"Relevant Sources: {', '.join(metadata.sources[:3])}...")
        print("-" * 80)

    print("\n" + "=" * 80)
    print("SYSTEM PROMPTS")
    print("=" * 80)

    print("\n[1] SYSTEM PROMPT - RAG Agent Definition:")
    print("-" * 80)
    print(RAGAgentPrompts.SYSTEM_PROMPT_DEFINITION())

    print("\n\n[2] OPERATION PROMPT - Routing & Triggers:")
    print("-" * 80)
    print(RAGAgentPrompts.OPERATION_PROMPT_ROUTING())
