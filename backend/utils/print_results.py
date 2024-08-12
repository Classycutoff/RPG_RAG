


def print_results(results):
    result_len = len(results['ids'][0])

    for i in range(result_len):
        metadata = results['metadatas'][0][i]
        print(f"""
Source: {metadata['source']}
Page: {metadata['page']}
Distance: {results['distances'][0][i]}

Document: {results['documents'][0][i]}
""")