from flask import Flask, render_template, request, jsonify
import uuid
from chatbot import get_answer

app = Flask(__name__)

# Dictionary to store chat sessions
chat_sessions = {}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Process a question and return an answer"""
    data = request.json
    question = data.get('text', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    language = data.get('language', 'en')
    
    if not question:
        return jsonify({'success': False, 'text': 'No question provided'}), 400
    
    try:
        # Get answer from your existing chatbot
        answer_text = get_answer(question, language)
        
        # Store in chat history
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
            
        chat_sessions[session_id].append({
            "question": question,
            "answer": answer_text
        })
        
        return jsonify({
            'text': answer_text,
            'success': True,
            'relevant_articles': []
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False, 
            'text': 'Sorry, there was an error processing your question.'
        }), 500

@app.route('/api/history/<session_id>')
def get_chat_history(session_id):
    """Return chat history for a session"""
    if session_id not in chat_sessions:
        return jsonify({
            'session_id': session_id,
            'history': []
        })
    
    return jsonify({
        'session_id': session_id,
        'history': chat_sessions[session_id]
    })

@app.route('/api/suggestions')
@app.route('/api/suggestions')
def get_suggestions():
    """Return suggested questions for the chatbot"""
    language = request.args.get('language', 'en')

    # Suggestion sets based on language
    suggestions_by_language = {
        'en': [
            "What are the fundamental principles of the Moroccan Constitution?",
            "What rights are guaranteed to Moroccan citizens?",
            "How is the government structured in Morocco?",
            "What is the role of the King in the Moroccan Constitution?",
            "How are laws passed in Morocco?"
        ],
        'fr': [
            "Quels sont les principes fondamentaux de la Constitution marocaine ?",
            "Quels droits sont garantis aux citoyens marocains ?",
            "Comment est structuré le gouvernement au Maroc ?",
            "Quel est le rôle du Roi dans la Constitution marocaine ?",
            "Comment les lois sont-elles adoptées au Maroc ?"
        ],
        'ar': [
            "ما هي المبادئ الأساسية للدستور المغربي؟",
            "ما هي الحقوق المضمونة للمواطنين المغاربة؟",
            "كيف يتم هيكلة الحكومة في المغرب؟",
            "ما هو دور الملك في الدستور المغربي؟",
            "كيف يتم سن القوانين في المغرب؟"
        ]
    }

    suggestions = suggestions_by_language.get(language, suggestions_by_language['en'])

    return jsonify({'suggestions': suggestions})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)