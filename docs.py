from googleapiclient.discovery import build
from authentication import authenticate




class GoogleDocsClient:
    def __init__(self):
        self.creds = authenticate()
        self.service = build('docs', 'v1', credentials=self.creds)
    
    def create_doc(self, name: str) -> dict:
        try:
            # Create document using Google client library
            doc = self.service.documents().create(
                body={'title': name}
            ).execute()
            
            return {
                'success': True,
                'doc_id': doc['documentId'],
                'title': doc['title'],
                'url': f"https://docs.google.com/document/d/{doc['documentId']}/edit"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_info_to_existing_doc(self, document_id: str, information: str, position: str = 'end', add_formatting: bool = False) -> dict:
        try:
            # Get document info first
            doc = self.service.documents().get(documentId=document_id).execute()
            content = doc.get('body', {}).get('content', [])

            # Find insertion point
            if position == 'beginning':
                insert_index = 1
            else:  # end
                insert_index = 1
                for element in content:
                    if 'endIndex' in element:
                        insert_index = element['endIndex']
            
                # KEY FIX: Subtract 1 from the end index to avoid the "must be less than" error
                # The endIndex points to the position after the last character, but we need to insert before that
                insert_index = max(1, insert_index - 1)

            requests = []

            # Add a line break before new content if not at beginning
            if position == 'end' and insert_index > 1:
                information = '\n\n' + information
                
            # Insert the text
            requests.append({
                'insertText': {
                'location': {'index': insert_index},
                'text': information
            }
        })
                  
            # Optional: Add formatting (bold headers, etc.)
            if add_formatting:
                # This would make the first line bold (assuming it's a header)
                first_line_end = information.find('\n')
                if first_line_end > 0:
                    requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': insert_index,
                            'endIndex': insert_index + first_line_end
                        },
                        'textStyle': {
                            'bold': True,
                            'fontSize': {'magnitude': 14, 'unit': 'PT'}
                        },
                        'fields': 'bold,fontSize'
                    }
                })
                         
            result = self.service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

            return {
            'success': True,
            'message': 'Content added successfully',
            'url': f'https://docs.google.com/document/d/{document_id}/edit'
        }
            
        except Exception as e:
            return {
            'success': False,
            'error': str(e)
        }