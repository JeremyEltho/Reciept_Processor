"""
RAG (Retrieval-Augmented Generation) model for receipt question answering.
"""

import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class ReceiptRAG:
    """RAG system for answering questions about receipt data."""
    
    def __init__(self):
        self.model = self._configure_gemini()
        self.receipt_context = None
    
    def _configure_gemini(self):
        """Configure the Gemini model."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    
    def load_receipt_context(self, receipt_data: dict):
        """Load receipt data as context for questions."""
        self.receipt_context = receipt_data
    
    def ask_question(self, question: str) -> str:
        """Ask a question about the loaded receipt data."""
        if not self.receipt_context:
            return "No receipt data loaded. Please upload and process a receipt first."
        
        # Prepare context from receipt data
        context = self._format_receipt_context()
        
        prompt = f"""You are a helpful assistant that answers questions about business receipts. 
You have access to the following receipt data:

{context}

User Question: {question}

Instructions:
- Answer the question based ONLY on the provided receipt data
- Be specific and reference actual values from the receipt
- If the information is not available in the receipt, say so clearly
- Keep responses concise but informative
- For monetary amounts, always include the currency symbol

Answer:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def _format_receipt_context(self) -> str:
        """Format receipt data into readable context."""
        if not self.receipt_context:
            return "No receipt data available."
        
        context = f"""
RECEIPT INFORMATION:
- Merchant: {self.receipt_context.get('merchant', 'N/A')}
- Date: {self.receipt_context.get('date', 'N/A')}
- Location: {self.receipt_context.get('location', 'N/A')}
- Total Amount: ${self.receipt_context.get('receipt_total', '0.00')}
- Subtotal: ${self.receipt_context.get('subtotal', '0.00')}
- Tax: ${self.receipt_context.get('tax', '0.00')}

ITEMS PURCHASED:
"""
        
        for i, item in enumerate(self.receipt_context.get('line_items', []), 1):
            context += f"""
{i}. {item.get('item', 'Unknown Item')}
   - Amount: ${item.get('amount', '0.00')}
   - Category: {item.get('category', 'Uncategorized')}
   - Justification: {item.get('justification', 'N/A')}
   - Needs Approval: {item.get('needs_approval', False)}
"""
        
        if self.receipt_context.get('flags'):
            context += f"\nFLAGS/ISSUES:\n"
            for flag in self.receipt_context['flags']:
                context += f"- {flag}\n"
        
        context += f"\nQuality Score: {self.receipt_context.get('completeness_score', 'N/A')}"
        context += f"\nProcessed: {self.receipt_context.get('processed_date', 'N/A')}"
        
        return context
    
    def get_suggested_questions(self) -> list:
        """Get suggested questions based on the receipt data."""
        if not self.receipt_context:
            return ["Please upload a receipt first to see suggested questions."]
        
        suggestions = [
            "What was the total amount spent?",
            "What items were purchased?",
            "What store was this from?",
            "When was this purchase made?",
            "Are there any items that need approval?",
            "What categories of expenses are included?",
            "How much tax was paid?",
            "What was the most expensive item?"
        ]
        
        # Add context-specific suggestions
        if self.receipt_context.get('flags'):
            suggestions.append("Are there any issues with this receipt?")
        
        if len(self.receipt_context.get('line_items', [])) > 1:
            suggestions.append("How many items were purchased?")
        
        return suggestions
