import urllib.parse
import xml.etree.ElementTree as ET
import requests
from typing import List, Dict, Any

class ArxivService:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"

    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers matching the given query and return parsed results.
        """
        # Clean and encode query
        safe_query = urllib.parse.quote(query.strip())
        url = f"{self.base_url}?search_query=all:{safe_query}&max_results={max_results}&sortBy=relevance&sortOrder=descending"
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"arXiv search error: HTTP {response.status_code}")
                return []
                
            return self._parse_xml(response.text)
        except Exception as e:
            print(f"arXiv search failed: {e}")
            return []

    def _parse_xml(self, xml_data: str) -> List[Dict[str, Any]]:
        """
        Parse arXiv Atom XML feed.
        """
        # arXiv returns Atom feed. Atom namespaces:
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        
        try:
            root = ET.fromstring(xml_data)
        except Exception as e:
            print(f"XML Parsing error: {e}")
            return []
            
        papers = []
        
        for entry in root.findall('atom:entry', namespaces):
            # Title
            title_node = entry.find('atom:title', namespaces)
            title = title_node.text.strip().replace('\n', ' ') if title_node is not None else "Unknown Title"
            
            # Summary/Abstract
            summary_node = entry.find('atom:summary', namespaces)
            summary = summary_node.text.strip().replace('\n', ' ') if summary_node is not None else "No abstract available"
            
            # Published Date
            published_node = entry.find('atom:published', namespaces)
            published = published_node.text.strip() if published_node is not None else ""
            
            # Authors
            authors = []
            for author_node in entry.findall('atom:author', namespaces):
                name_node = author_node.find('atom:name', namespaces)
                if name_node is not None:
                    authors.append(name_node.text.strip())
            authors_str = ", ".join(authors) if authors else "Unknown Authors"
            
            # Document ID and PDF Link
            id_node = entry.find('atom:id', namespaces)
            arxiv_id = ""
            if id_node is not None:
                arxiv_id = id_node.text.split('/abs/')[-1].split('v')[0] # Get ID like '2303.17760'
                
            pdf_url = ""
            for link in entry.findall('atom:link', namespaces):
                title_attr = link.attrib.get('title')
                type_attr = link.attrib.get('type')
                href = link.attrib.get('href', '')
                
                # Check for PDF links
                if type_attr == 'application/pdf' or 'pdf' in href:
                    pdf_url = href
                    if not pdf_url.endswith('.pdf'):
                        pdf_url += ".pdf"
            
            # Fallback if no PDF link explicitly found
            if not pdf_url and arxiv_id:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
            papers.append({
                "id": arxiv_id,
                "title": title,
                "authors": authors_str,
                "abstract": summary,
                "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
                "pdf_url": pdf_url,
                "published": published
            })
            
        return papers
