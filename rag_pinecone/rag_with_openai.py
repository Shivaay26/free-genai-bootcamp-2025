from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai

# Initialize Pinecone
pc = Pinecone(api_key="pcsk_5T7Wk1_7w6ZKBQjDA9m1dvRsnLPPdkaaXhmSrcyxigEp85Dc2p8Fmkgh26wC56p3XWV9DT")

# Initialize Gemini - FIXED: Use genai.configure() instead of genai.Client()
genai.configure(api_key="AIzaSyAahQOY4zZlvrhULEfjy0g4bFRi8ReZwTA")

def get_response(query: str, index_name: str, top_k: int = 3):
    # Get index
    index = pc.Index(index_name)
    
    # Query Pinecone
    results = index.search(
        namespace="default",
        query={
            "top_k": top_k,
            "inputs": {
                "text": query
            }
        }
    )
    
    print(f"Results type: {type(results)}")
    print(f"Results content: {results}")
    print(f"Results matches: {results.matches}")
    
    # Create context from documents
    if results.matches:
        docs = results.matches
        context = "\n".join([doc.metadata.text for doc in docs if doc.metadata and hasattr(doc.metadata, 'text')])
    else:
        context = "No relevant documents found."
    
    # Create system prompt
    system_prompt = f"""
    You are a helpful AI assistant. Use the following context to answer the question.
    If the context is not relevant, just answer the question to the best of your ability.
    
    Context:
    {context}
    """
    
    # Get response from Gemini - FIXED: Use genai.GenerativeModel and correct method calls
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Updated model name
        
        # FIXED: Use generate_content with proper format
        response = model.generate_content(f"{system_prompt}\n\nUser Question: {query}")
        
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Example usage
if __name__ == "__main__":
    index_name = "developer-quickstart-py"
    query = "Famous historical structures and monuments"
    response = get_response(query, index_name)
    print(response)