# BM25: An Advanced Ranking Algorithm for Document Retrieval Systems

## Introduction to BM25 and Document Retrieval

### Defining BM25: Best Matching 25
BM25, an acronym for Best Matching 25, also known as Okapi BM25, represents a fundamental and widely adopted scoring and ranking algorithm within the field of information retrieval. Operating as a probabilistic model, its primary function is to assess the degree to which a document aligns with a given search query, thereby estimating the document's relevance [^4], [^10]. This robust method computes a relevance score by intricately considering several factors: the frequency of terms within a document (term frequency), the overall length of the document, and the inverse document frequency (IDF) of the query terms [^5], [^11], [^17]. Unlike simpler approaches, BM25 incorporates free parameters, typically *k1* (commonly set between 1.2 and 2.0) and *b* (usually 0.75), which allow for fine-tuning its calculation and provide control over aspects like term frequency saturation and document length normalization [^12], [^18], [^64].

### Role in Information Retrieval and Search Engines
Okapi BM25 plays a pivotal role in modern information retrieval systems and search engines by serving as a sophisticated ranking function. Its core utility lies in its ability to effectively estimate and determine the relevance of vast numbers of documents to a user's specific search query [^10], [^16]. BM25 is crucial for balancing the influence of term frequency, document frequency, and document length, ensuring that longer documents do not inherently receive inflated scores without genuine relevance [^17], [^190]. This balanced approach distinguishes it as an advanced method for scoring. Beyond traditional search, BM25 is increasingly integrated into contemporary systems, such as Azure AI Search for keyword search [^18], and is notably combined with Large Language Models (LLMs) to enhance search and retrieval performance in applications like Retrieval-Augmented Generation (RAG) [^4], [^265]. Its speed and precision also enable it to function as an initial filter in hybrid retrieval architectures, such as those combining BM25 with FAISS for semantic refinement [^235], [^249].

### Evolution of Ranking Algorithms
BM25 signifies a significant evolution in the landscape of document ranking algorithms, building upon and improving previous models like TF-IDF (Term Frequency-Inverse Document Frequency) [^5], [^28]. While TF-IDF provides a straightforward method for weighting terms based on their frequency and rarity, BM25 introduces more advanced and fine-tuned mechanisms [^29]. Key improvements include its sophisticated handling of term frequency saturation, which prevents excessively high term frequencies from disproportionately inflating a document's score [^208], [^211]. Additionally, BM25 incorporates a robust mechanism for document length normalization, ensuring that a document's length does not unduly bias its relevance score, a limitation often observed in simpler models [^17], [^196]. These enhancements contribute to BM25 being considered a more robust, effective, and nuanced ranking algorithm than its predecessors, making it a preferred choice for achieving accurate and detailed search results [^30], [^307].

## Understanding How BM25 Works

### Probabilistic Model and Relevance Scoring
Okapi BM25, also known as Best Matching 25, stands as a widely utilized scoring and ranking algorithm within information retrieval systems. It operates as a probabilistic model, with its primary function being to assess how effectively a document aligns with a given search query, thereby estimating the document's relevance. As an evolution of earlier models like TF-IDF, BM25 addresses some of their inherent limitations by incorporating factors such as term frequency, document length, and inverse document frequency (IDF) to compute a precise relevance score [^4], [^10]. BM25 is designed to be a robust method for scoring, balancing these elements and crucially normalizing for document length to ensure longer documents do not receive disproportionately higher scores merely due to their length [^16]. This model also integrates frequency saturation, distinguishing it from simpler approaches like TF-IDF [^16], [^208].

### The BM25 Mathematical Formula
The Okapi BM25 ranking function is employed by search engines to estimate the relevance of documents to a given query, extending the capabilities of TF-IDF by considering term frequency saturation and document length. Given a query Q containing keywords q1 through qn, the BM25 score of a document D is calculated using the following formula [^118]:

${\displaystyle {\text{score}}(D,Q)=\sum _{i=1}^{n}{\text{IDF}}(q_{i})\cdot {\frac {f(q_{i},D)\cdot (k_{1}+1)}{f(q_{i},D)+k_{1}\cdot \left(1-b+b\cdot {\frac {|D|}{\text{avgdl}}}\right)}}}$

This formula allows for a nuanced assessment of document relevance, factoring in several critical components and free parameters to achieve its robust ranking capability [^70], [^118].

### Components of the Formula: f(qi,D), |D|, avgdl, IDF(qi)
Within the BM25 formula, several key components are crucial for calculating the relevance score. $f(q_i, D)$ represents the term frequency, indicating how many times the query term $q_i$ appears within document D [^64], [^118]. $|D|$ signifies the length of document D, typically measured in words, while $avgdl$ refers to the average document length across the entire corpus of documents being searched [^118]. $IDF(q_i)$ is the Inverse Document Frequency weight for the query term $q_i$, which reflects the rarity of the term across the corpus; terms that appear in fewer documents generally have a higher IDF weight [^64], [^76], [^118]. Additionally, the formula includes two free parameters: $k_1$ and $b$. The parameter $k_1$ controls term frequency saturation, typically ranging from 1.2 to 2.0. A higher $k_1$ value allows multiple occurrences of a term to contribute more significantly to the score before saturation [^64], [^76], [^166]. The parameter $b$ dictates the impact of document length normalization, commonly set to 0.75. A value of 0 for $b$ means no length normalization, while 1 signifies full normalization, preventing longer documents from gaining an unfair advantage merely due to their length [^64], [^76], [^184], [^196].

### Derivation from Probabilistic Models (e.g., Binary Independence Model)
Okapi BM25 is rooted in the family of probabilistic information retrieval models, specifically deriving its foundations from the Binary Independence Model (BIM) [^10], [^40], [^58]. The Inverse Document Frequency (IDF) component, a crucial part of the BM25 formula, is directly derived from the BIM [^34], [^40]. While BIM serves as a conceptual framework for assessing document relevance, BM25 extends this model significantly. It incorporates within-document term frequency information, document length normalization, and additional document and query term weights, which are not present in the basic BIM [^46]. BM25's design, including its free parameters like $k_1$ and $b$, allows it to approximate the BIM model more closely when adjusted appropriately [^52]. This robust derivation underpins BM25's effectiveness as a ranking algorithm [^58].

## Key Parameters and Their Impact

The effectiveness of the BM25 algorithm in ranking documents hinges significantly on two critical free parameters: `k1` and `b`. These parameters allow for fine-tuning the algorithm's behavior to specific corpora and retrieval needs, influencing how term frequency and document length contribute to a document's relevance score [^10][^16][^22][^64][^70][^76][^82][^118].

### The k1 Parameter: Term Frequency Saturation and Non-Linear Weighting

The `k1` parameter in BM25 is central to controlling term frequency saturation and implementing non-linear weighting of terms within a document. It dictates how quickly the relevance score for a document increases as a query term appears more frequently within it [^166][^211][^229]. Unlike simpler models that might linearly increase a score with every term occurrence, BM25, through `k1`, employs a non-linear approach that prevents excessively high term frequencies from disproportionately inflating a document's score [^208][^217][^223]. A higher value for `k1` allows term frequency to continue contributing more significantly to the score for a longer period before it "saturates" or levels off. Conversely, if `k1` is set to 0, term frequency has no impact, and only the Inverse Document Frequency (IDF) of the search term contributes to the score [^154]. This mechanism ensures a balanced and nuanced approach to relevance scoring, differentiating BM25 from less sophisticated methods like TF-IDF [^28][^208].

### The b Parameter: Document Length Normalization

The `b` parameter is crucial for document length normalization within the BM25 scoring function. Its primary role is to adjust scores based on a document's length, preventing longer documents from inherently receiving higher relevance scores simply because they contain more terms [^190][^202]. This mechanism is a key differentiator from simpler models like TF-IDF, which might inadvertently favor longer documents [^28][^196]. The `b` parameter controls the degree of this normalization, ranging from 0 to 1. When `b` is set to 0, no document length normalization is applied, meaning document length does not affect the score [^106][^196]. Conversely, when `b` is set to 1, the document's term frequency component is fully normalized based on its length [^184][^196]. A higher `b` value leads to a greater penalization for longer documents, requiring them to have a slightly higher term frequency to achieve the same relevance score as shorter ones [^184]. This ensures fairer relevance scoring across documents of varying lengths [^178][^192].

### Empirical Basis and Tuning Guidelines for k1 and b

The `k1` and `b` parameters are free parameters within the BM25 scoring function, commonly chosen based on empirical observations and dataset characteristics [^10][^64][^70][^76][^82][^118]. While the IDF component of BM25 is rooted in the Binary Independence Model (BIM), the overall BM25 model extends BIM by incorporating term frequency, document length normalization, and additional term weights, with `k1` and `b` allowing the model to approximate the BIM more closely [^40][^46][^52].

Typical values for `k1` are commonly observed in the range of 1.2 to 2.0, while `b` is frequently set to 0.75 [^10][^16][^22][^64][^70][^76][^82][^100][^106][^118]. For instance, Apache Lucene specifically uses `k1 = 1.2` and `b = 0.75` [^100]. However, the optimal values for these parameters are highly dependent on the specific data collection or corpus being used [^172]. While dedicated parameter tuning can be performed—for example, Elasticsearch has explored `k1` values between 0 and 3 [^148]—initial efforts to optimize relevance in search systems are often better spent on implementing more expressive query languages, linguistic controls, and incorporating user feedback. Deeply adjusting `k1` and `b` might be considered after these broader relevance features have been addressed [^148][^172].

## BM25 vs. TF-IDF: An Evolution in Ranking

### TF-IDF: The Predecessor
TF-IDF (Term Frequency-Inverse Document Frequency) stands as a foundational method in information retrieval, primarily used for weighting terms based on their frequency within a document and their rarity across an entire corpus. It provides a simple yet effective approach to assess the importance of a word to a document in a collection [^28]. This method calculates a score for each term, considering how often it appears in a document (Term Frequency) and how unique it is across all documents (Inverse Document Frequency), thereby identifying terms that are significant to a specific document without being overly common [^28].

### Addressing TF-IDF Limitations
While TF-IDF laid crucial groundwork, BM25 (Best Matching 25), also known as Okapi BM25, emerged as a significant evolution and improvement in ranking algorithms [^5], [^28]. As a probabilistic model, BM25 addresses several limitations inherent in simpler predecessors like TF-IDF [^5], [^10]. Specifically, BM25 introduces advanced considerations such as document length normalization and sophisticated handling of term frequency, which TF-IDF does not fully account for [^16], [^28]. This allows BM25 to provide a more nuanced and accurate assessment of document relevance [^28].

### Frequency Saturation and its Importance
A key differentiator for BM25 is its consideration of frequency saturation, a feature absent in simpler methods such as TF-IDF [^16], [^208]. Frequency saturation refers to the diminishing returns of a term's relevance score as its frequency within a document increases beyond a certain point [^166]. BM25 incorporates a non-linear term frequency weighting, controlled by the `k1` parameter, to manage this saturation [^223], [^229]. The `k1` parameter, typically set between 1.2 and 2.0, determines how quickly the relevance score levels off with increasing term frequency, preventing excessively high term counts from disproportionately inflating a document's score [^100], [^166], [^208]. This mechanism ensures a more balanced and realistic contribution of term frequency to the overall relevance score [^229].

### Superiority in Document Relevance
Overall, BM25 is widely recognized as a more robust and effective ranking algorithm than TF-IDF, making it a preferred choice for achieving detailed and accurate results in modern search engines [^28], [^208]. Its superiority stems from its ability to balance various factors more effectively, including term frequency, document length, and the crucial element of frequency saturation [^16], [^295]. By normalizing for document length, BM25 ensures that longer documents do not inherently receive higher scores simply due to their length, unless they are genuinely more relevant [^28], [^190]. This comprehensive approach allows BM25 to provide a fine-tuned method for estimating document relevance, offering a significant advancement over the basic weighting scheme of TF-IDF [^28].

## Real-World Applications and Implementations of BM25

### Standalone Re-ranking and Speed Considerations
Okapi BM25, also known as Best Matching 25, is a robust and widely utilized ranking function in information retrieval systems that can be effectively deployed as a standalone document re-ranker [^22, ^253]. Compared to more computationally intensive models, such as BERT-based scoring, BM25 offers significant speed advantages, completing tasks in seconds versus minutes [^22]. This efficiency is partly attributed to its computational complexity, which is O(n), aligning with other relevance scoring models [^289, ^301]. BM25's design allows it to balance factors like term frequency, document length, and inverse document frequency while maintaining computational efficiency [^307]. Although its free parameters, `k1` and `b`, can be tuned for specific data collections, initial optimization efforts might yield greater returns when focused on other relevance features like expressive query languages or linguistic controls [^148, ^172]. Furthermore, BM25 can convert documents and queries into sparse vectors, facilitating efficient storage and retrieval in vector databases [^295, ^313].

### Hybrid Retrieval with Vector Databases (e.g., FAISS)
To enhance document retrieval and improve Retrieval-Augmented Generation (RAG) system performance, BM25 is frequently combined with vector databases like FAISS in hybrid retrieval architectures [^235, ^247]. This approach leverages BM25's strength in precise keyword-based retrieval, often using it as an initial filter to narrow down results. Subsequently, FAISS applies semantic refinement, capturing contextual relationships through dense retrieval methods [^235, ^247, ^253]. The workflow typically involves indexing documents, followed by BM25 performing an initial keyword-based search. FAISS then conducts searches to capture semantic relationships, and the results from both are merged to provide highly relevant documents [^259]. This integration forms a powerful system that maximizes both efficiency and relevance, bridging traditional keyword understanding with contextual comprehension [^241, ^247]. An “EnsembleRetriever” can be utilized to combine these distinct components [^241].

### Integration with Large Language Models (LLMs) in RAG Systems
BM25 plays a crucial role in enhancing the retrieval step within Retrieval-Augmented Generation (RAG) systems that leverage Large Language Models (LLMs) [^4, ^265, ^271]. As an efficient term-based ranking model, BM25 is utilized to retrieve a set of relevant passages or documents from data sources based on a user query [^271, ^277]. In a RAG pipeline, BM25 search results are often combined with those from vector database searches, leveraging methods like Reciprocal Rank Fusion (RRF) to integrate scores from multiple retrieval techniques and boost overall retrieval performance [^265, ^277, ^283]. Once these relevant passages are retrieved, the LLM processes them for semantic understanding, summarization, and to generate a comprehensive, contextually relevant answer to the user's query [^271, ^283]. This combination of BM25 for efficient keyword-based retrieval and LLMs for advanced semantic processing allows RAG systems to overcome the limitations of pure LLMs by effectively handling large and dynamic datasets, thereby improving overall search and retrieval capabilities [^271, ^295].

## Performance and Scalability of BM25

### Computational Complexity and Efficiency
BM25 exhibits a computational complexity of O(n), aligning with other relevance scoring models [^289, ^290, ^291]. This efficiency is a key characteristic, especially when compared to more computationally intensive methods like BERT-based scoring, where BM25 can operate significantly faster—in seconds versus minutes for re-ranking tasks [^22, ^23, ^24]. As an evolution of earlier models like TF-IDF, BM25 maintains computational efficiency while improving relevance scoring by effectively balancing factors such as term frequency, document frequency, and document length [^295, ^296, ^297, ^301, ^302, ^303, ^307, ^308, ^309]. Its robust design allows it to enhance search results by normalizing scores to prevent longer documents from unduly dominating rankings [^295, ^296, ^297].

### Indexing Strategies (e.g., Inverted Lists)
The scalability and performance of BM25 are inherently tied to its underlying data structures and implementation strategies. The algorithm commonly relies on an in-memory inverted list data structure, which facilitates efficient document retrieval [^313, ^314, ^315]. Beyond standalone implementations, BM25 plays a crucial role in hybrid retrieval architectures, such as those combining it with FAISS. In such systems, BM25 often serves as an initial filter for precise keyword-based retrieval, narrowing down results before dense retrieval methods like FAISS apply semantic refinement [^22, ^23, ^24, ^235, ^236, ^237, ^247, ^248, ^249, ^259, ^260, ^261]. This “sparse” retrieval capability, focusing on exact keyword matches, complements “dense” retrieval techniques that use vector embeddings for semantic understanding [^241, ^242, ^243]. The process typically involves indexing documents, performing searches with both components, and then merging the results to maximize both efficiency and relevance [^235, ^236, ^237]. Furthermore, BM25 can be used to convert documents and queries into sparse vectors, which can be stored and retrieved efficiently in scalable vector databases like Milvus [^295, ^296, ^297, ^313, ^314, ^315].

### Memory Considerations
Memory usage is a significant factor in the scalability of BM25, particularly given its reliance on in-memory inverted list data structures [^313, ^314, ^315]. The efficiency of BM25 implementations can be affected by memory overheads and the pressures associated with memory allocation requests, such as `malloc` calls for postings lists [^313, ^314, ^315]. To address scalability and memory concerns, BM25 can be adapted to represent documents and queries as sparse vectors. This approach allows for their efficient storage and retrieval within vector databases like Milvus, thereby facilitating operations across large datasets [^295, ^296, ^297, ^313, ^314, ^315].

## Limitations and Future Directions

### Inherent Limitations (e.g., Semantic Understanding)
As an evolution of TF-IDF and a probabilistic model derived from the Binary Independence Model, BM25 excels in keyword-based retrieval by balancing factors such as term frequency, document length, and inverse document frequency to estimate relevance [^4], [^16], [^34], [^40]. However, its strength in precise keyword matching also highlights an inherent limitation: a lack of semantic understanding. BM25 primarily evaluates documents based on the statistical occurrence and distribution of terms, meaning it does not inherently grasp the deeper meaning, context, or semantic relationships between words [^241], [^271]. This can lead to challenges in scenarios involving synonyms, polysemy, or queries where the intent is not explicitly expressed through keywords, as it struggles to retrieve documents that are contextually relevant but do not contain the exact query terms [^241]. While robust for term weighting and length normalization, its foundation does not extend to the nuanced comprehension of language that semantic models provide [^16], [^217].

### Addressing Limitations and Future Enhancements
To overcome its inherent limitations, particularly regarding semantic understanding, BM25 is increasingly integrated into advanced and hybrid retrieval architectures. One significant approach involves combining BM25 with dense retrieval methods, such as those employing FAISS, to create hybrid search systems [^23], [^235]. In such a pipeline, BM25 often serves as an efficient initial filter, narrowing down results based on precise keyword matches, while FAISS then applies semantic refinement using vector embeddings to capture contextual relationships [^23], [^247], [^253]. This orchestrated workflow typically involves indexing documents, performing searches with both methods, and then merging the results to deliver highly relevant documents that benefit from both keyword precision and semantic understanding [^235], [^259].

Furthermore, BM25 plays a vital role in Retrieval-Augmented Generation (RAG) systems that leverage Large Language Models (LLMs) [^4], [^295]. In this architecture, BM25 efficiently retrieves a set of relevant passages or documents based on a user query [^271]. These retrieved passages are then fed to an LLM, which processes them for semantic understanding, summarization, and to generate comprehensive and contextually relevant answers [^271], [^277], [^283]. This synergy allows LLMs to handle large and dynamic datasets by grounding their generative capabilities in retrieved information, effectively addressing BM25's limitations in semantic comprehension [^271]. Methods like Reciprocal Rank Fusion (RRF) are also employed to boost retrieval performance by intelligently combining scores from multiple retrieval methods, including BM25 and vector database searches [^265], [^277]. Beyond system integrations, ongoing optimization of BM25's free parameters, `k1` (controlling term frequency saturation) and `b` (governing document length normalization), allows for fine-tuning its performance to specific data collections, though broader relevance features may offer more substantial gains [^148], [^172], [^196]. BM25's computational efficiency and scalability further ensure its continued relevance as a core component in complex, high-performance information retrieval systems [^289], [^307], [^313].

## Conclusion

### Summary of BM25's Impact
BM25, or Best Matching 25, stands as a cornerstone in the field of information retrieval, functioning as a sophisticated probabilistic model widely adopted by search engines to gauge document relevance against a given query [^4], [^10]. This algorithm represents a significant evolution from simpler term-weighting schemes like TF-IDF, systematically addressing their limitations by integrating advanced factors such as term frequency saturation and robust document length normalization [^28], [^29], [^30]. BM25's mathematical foundation is rooted in the Binary Independence Model (BIM), which informs its Inverse Document Frequency (IDF) component, while extending it to incorporate within-document term frequency information and document length adjustments [^34], [^40], [^46].

A key strength of BM25 lies in its carefully balanced parameters, notably `k1` (typically 1.2-2.0) and `b` (commonly 0.75), which control term frequency contribution and document length normalization, respectively [^64], [^70], [^76]. The `k1` parameter dictates how quickly the relevance score saturates as a term appears more frequently, preventing undue weight from excessively repeated terms [^166], [^208]. Concurrently, the `b` parameter ensures that longer documents are not inherently favored, normalizing scores relative to the average document length within the corpus [^178], [^190], [^196]. This nuanced approach has cemented BM25's reputation as a robust and effective ranking algorithm, consistently outperforming simpler methods in delivering accurate search results [^28], [^30]. Furthermore, BM25 maintains computational efficiency, exhibiting a complexity of O(n), making it highly practical for large-scale document retrieval systems [^289], [^301], [^307].

### Future Directions in Document Retrieval
The enduring relevance of BM25 is evident in its continued integration into cutting-edge document retrieval systems, particularly alongside advancements in artificial intelligence. A significant direction involves its combination with Large Language Models (LLMs) in Retrieval-Augmented Generation (RAG) architectures [^4], [^265]. In such a pipeline, BM25 typically serves as an efficient initial retriever, identifying relevant passages or documents based on keyword matching. These retrieved results are then fed to an LLM, which processes the information for deeper semantic understanding, summarization, and to generate comprehensive and contextually rich answers [^271], [^272], [^273].

Beyond RAG, BM25 is a critical component in hybrid retrieval systems that merge traditional keyword-based search with modern semantic search. For instance, in a BM25-FAISS hybrid architecture, BM25 acts as an initial filter, precisely narrowing down results based on keywords, before semantic refinement is applied by FAISS through vector embeddings [^235], [^247], [^253]. This combination leverages BM25's precision for exact matches and FAISS's ability to capture contextual relationships, culminating in a more powerful and nuanced retrieval system [^253], [^259]. Techniques such as Reciprocal Rank Fusion (RRF) are also employed to effectively combine scores from BM25 and vector database searches, further boosting retrieval performance [^265], [^277], [^283]. As the volume and complexity of information continue to grow, BM25's adaptability, computational efficiency, and robust ranking capabilities ensure its foundational role in the evolving landscape of intelligent information retrieval and generative AI applications.

## Sources

[^4]: [What is BM25 (Best Matching 25) Algorithm? - GeeksforGeeks](https://www.geeksforgeeks.org/what-is-bm25-best-matching-25-algorithm/)
[^5]: [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
[^6]: [Understanding Okapi BM25: A Guide to Modern Information Retrieval](https://adasci.org/understanding-okapi-bm25-a-guide-to-modern-information-retrieval/)
[^12]: [What Is BM25 (Best Match 25): Full Breakdown - Luigi's Box](https://www.luigisbox.com/search-glossary/bm25/)
[^16]: [What is BM25? - Online Marketing Consulting](https://www.kopp-online-marketing.com/what-is-bm25)
[^18]: [BM25 relevance scoring - Azure AI Search - Microsoft Learn](https://learn.microsoft.com/en-us/azure/search/index-similarity-and-scoring)
[^22]: [Implementing Hybrid Retrieval (BM25 + FAISS) in RAG - Chitika](https://www.chitika.com/hybrid-retrieval-rag/)
[^24]: [BM25 vs. BERT for Information Retrieval - GitHub](https://github.com/paulmelki/BERT_BM25_InformationRetrieval)
[^29]: [Comparing BM25 vs TF-IDF: Which is Better?](https://myscale.com/blog/bm25-vs-tf-idf-deep-dive-comparison/)
[^30]: [How BM25 improves upon TF-IDF : r/AIMadeSimple](https://www.reddit.com/r/AIMadeSimple/comments/16nq6x7/how_bm25_improves_upon_tfidf/)
[^34]: [Sparse Vector Using BM25 - LinkedIn](https://www.linkedin.com/pulse/sparse-vector-using-bm25-jose-r-f-junior-h6uwf)
[^35]: [Implementing a search engine in ruby (learning purpose only)](https://www.andrewsaguiar.com/blog/2020/05/12/text-search-implementing-a-search-engine-in-ruby-learning-purpose-only)
[^36]: [Which BM25 Do You Mean? A Large-Scale Reproducibility Study of ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC7148026/)
[^42]: [[PDF] 1 LSI 2 Binary Independence Model](https://www.cs.purdue.edu/homes/clifton/cs473/Asn3Sol.pdf)
[^48]: [Retrieval models I](https://www.cs.cornell.edu/courses/cs4300/2013fa/lectures/retrieval-models-1-4pp.pdf)
[^52]: [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
[^54]: [Understanding the BM25 Ranking Algorithm - AI Mind](https://pub.aimind.so/understanding-the-bm25-ranking-algorithm-19f6d45c6ce)
[^59]: [14. Binary Independence Model (BIM)](https://www.youtube.com/watch?v=uuM3PTvecEY)
[^60]: [The Probabilistic Relevance Framework: BM25 and Beyond](https://www.nowpublishers.com/article/Details/INR-019)
[^64]: [bm25_intro - GitHub Pages](https://ethen8181.github.io/machine-learning/search/bm25_intro.html)
[^65]: [BM25 and Its Role in Document Relevance Scoring - Sourcely](https://www.sourcely.net/resources/bm25-and-its-role-in-document-relevance-scoring)
[^66]: [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
[^71]: [What Is BM25 (Best Match 25): Full Breakdown](https://www.luigisbox.com/search-glossary/bm25/)
[^72]: [Understanding Okapi BM25 — Document Ranking algorithm](https://medium.com/@readwith_emma/understanding-okapi-bm25-document-ranking-algorithm-70d81adab001)
[^76]: [What is BM25? The Ranking Formula Behind Search Engines](https://arshad404.medium.com/what-is-bm25-the-ranking-formula-behind-search-engines-c9c79c0a0dbd?source=rss------ai-5)
[^78]: [Practical BM25 - Part 2: The BM25 Algorithm and its Variables - Elastic](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
[^84]: [What is BM25 (Best Matching 25) Algorithm? - GeeksforGeeks](https://www.geeksforgeeks.org/what-is-bm25-best-matching-25-algorithm/)
[^90]: [Scoring Methods in Information Retrieval: A Linear Algebra ...](https://escholarship.org/content/qt5xp6h0nz/qt5xp6h0nz_noSplash_2d53a6488b24a768c6ab4f5ba3d38054.pdf?t=ml509x)
[^94]: [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
[^95]: [BM25 Retriever - LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/retrievers/bm25_retriever/)
[^96]: [Understanding Okapi BM25 — Document Ranking algorithm - Medium](https://medium.com/@readwith_emma/understanding-okapi-bm25-document-ranking-algorithm-70d81adab001)
[^101]: [Okapi BM25 with Game of Thrones - mimacom blog](https://blog.mimacom.com/bm25-got/)
[^102]: [[PDF] CS630 Lecture 6: The BM25/Okapi method - CS@Cornell](https://www.cs.cornell.edu/courses/cs630/2006sp/guides/lec6.kr.pdf)
[^107]: [Practical BM25 - Part 3: Considerations for Picking b and ...](https://www.elastic.co/blog/practical-bm25-part-3-considerations-for-picking-b-and-k1-in-elasticsearch)
[^108]: [Practical BM25 - Part 2: The BM25 Algorithm and its ...](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
[^113]: [bm25_intro - GitHub Pages](https://ethen8181.github.io/machine-learning/search/bm25_intro.html)
[^118]: [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
[^119]: [Understanding TF-IDF and BM-25 - KMW Technology](https://kmwllc.com/index.php/2020/03/20/understanding-tf-idf-and-bm-25/)
[^120]: [TF-IDF and BM25 for RAG— a complete guide - AI Bites](https://www.ai-bites.net/tf-idf-and-bm25-for-rag-a-complete-guide/)
[^124]: [Improved VSM Instantiation - Okapi BM25 - immersinn-ds](https://immersinn.github.io/okapi-bm25.html)
[^126]: [Understanding Okapi BM25 — Document Ranking algorithm - Medium](https://medium.com/@readwith_emma/understanding-okapi-bm25-document-ranking-algorithm-70d81adab001)
[^130]: [What is BM25 (Best Matching 25) Algorithm?](https://www.geeksforgeeks.org/what-is-bm25-best-matching-25-algorithm/)
[^137]: [BM25 Retriever - LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/retrievers/bm25_retriever/)
[^143]: [What is BM25? - Online Marketing Consulting](https://www.kopp-online-marketing.com/what-is-bm25)
[^148]: [Optimizing BM25 for Document Retrieval](https://prosperasoft.com/blog/artificial-intelligence/optimizing-bm25-for-document-retrieval/)
[^149]: [How to choose the OKAPI BM25 parameters : b and k1](https://stackoverflow.com/questions/38071877/how-to-choose-the-okapi-bm25-parameters-b-and-k1)
[^150]: [Practical BM25 - Part 3: Considerations for Picking b and ...](https://www.elastic.co/blog/practical-bm25-part-3-considerations-for-picking-b-and-k1-in-elasticsearch)
[^155]: [Practical BM25 - Part 2: The BM25 Algorithm and its Variables - Elastic](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
[^156]: [Understanding Okapi BM25: A Guide to Modern Information Retrieval](https://adasci.org/understanding-okapi-bm25-a-guide-to-modern-information-retrieval/)
[^161]: [How do I tune the performance of Haystack's retrieval algorithms?](https://milvus.io/ai-quick-reference/how-do-i-tune-the-performance-of-haystacks-retrieval-algorithms)
[^166]: [Keyword Search (BM25) | Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/search/keyword-search)
[^168]: [Unlocking the Power of BM25: Why It's Outshining TF-IDF in the ...](https://medium.com/@kushagramisra10/unlocking-the-power-of-bm25-why-its-outshining-tf-idf-in-the-world-of-search-152413392790)
[^178]: [Verboseness Fission for BM25 Document Length Normalization](http://aldolipani.com/wp-content/uploads/2015/08/ICTIRa.pdf)
[^179]: [BM25 and Its Role in Document Relevance Scoring - Sourcely](https://www.sourcely.net/resources/bm25-and-its-role-in-document-relevance-scoring)
[^180]: [Unlocking the Power of BM25: Why It's Outshining TF-IDF in the ...](https://medium.com/@kushagramisra10/unlocking-the-power-of-bm25-why-its-outshining-tf-idf-in-the-world-of-search-152413392790)
[^184]: [Support BM25 parameters customization · Issue #163 - GitHub](https://github.com/lucaong/minisearch/issues/163)
[^185]: [[PDF] The Effect of Query Length on Normalisation in Information Retrieval](https://www.dcs.gla.ac.uk/~ronanc/papers/cumminsAICS09.pdf)
[^192]: [What is BM25? - Online Marketing Consulting](https://www.kopp-online-marketing.com/what-is-bm25)
[^198]: [Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25)
[^203]: [BM25S — Efficacy Improvement of BM25 Algorithm in Document ...](https://medium.com/data-science/bm25s-efficacy-improvement-of-bm25-algorithm-in-document-retrieval-7c27ba665b7e)
[^204]: [BM25 Search | SAP Help Portal](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-predictive-analysis-library/bm25-search)
[^208]: [What is BM25? - Online Marketing Consulting](https://www.kopp-online-marketing.com/what-is-bm25)
[^209]: [Unlocking the Power of BM25: Why It's Outshining TF-IDF in the ...](https://medium.com/@kushagramisra10/unlocking-the-power-of-bm25-why-its-outshining-tf-idf-in-the-world-of-search-152413392790)
[^210]: [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
[^211]: [Keyword Search (BM25) | Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/search/keyword-search)
[^212]: [Optimizing BM25 for Document Retrieval - Prospera Soft](https://prosperasoft.com/blog/artificial-intelligence/optimizing-bm25-for-document-retrieval/)
[^218]: [BM25 and Its Role in Document Relevance Scoring - Sourcely](https://www.sourcely.net/resources/bm25-and-its-role-in-document-relevance-scoring)
[^219]: [Understanding Okapi BM25: A Guide to Modern Information Retrieval](https://adasci.org/understanding-okapi-bm25-a-guide-to-modern-information-retrieval/)
[^224]: [BM25t: a BM25 extension for focused information retrieval](https://hal.science/hal-00617973/document)
[^225]: [Simple BM25 extension to multiple weighted fields](https://dl.acm.org/doi/pdf/10.1145/1031171.1031181)
[^235]: [Implementing Hybrid Retrieval (BM25 + FAISS) in RAG - Chitika](https://www.chitika.com/hybrid-retrieval-rag/)
[^236]: [Hybrid Retrieval with FAISS & BM25 - Prospera Soft](https://prosperasoft.com/blog/artificial-intelligence/rag/hybrid-retrieval-with-faiss-bm25/)
[^237]: [Advanced Techniques to Build Your RAG System](https://machinelearningmastery.com/advanced-techniques-to-build-your-rag-system/)
[^241]: [A Practical Guide to Hybrid Search - CelerData](https://celerdata.com/glossary/hybrid-search)
[^242]: [BM25 and FAISS hybrid search example - GitHub Gist](https://gist.github.com/breadchris/b73aae81953eb8f865ebb4842a1c15b5)
[^243]: [Hybrid Search Made Easy: BM25 + OpenAI Embeddings | Medium](https://photokheecher.medium.com/hybrid-search-made-easy-bm25-openai-embeddings-34e16a08cc17)
[^248]: [How to Implement a Hybrid Search RAG Pipeline using FAISS and ...](https://www.edureka.co/community/311229/how-implement-hybrid-search-rag-pipeline-using-faiss-and-bm25)
[^260]: [Building a Clinical RAG System with Gemma-3, FAISS, and BM25](https://medium.com/@mhusnain3133/building-a-clinical-rag-system-with-gemma-3-faiss-and-bm25-eb2ef223ed45)
[^265]: [Boosting Retrieval in RAG for LLMs: The Power of BM25 and RRF](https://dkaarthick.medium.com/boosting-retrieval-in-rag-for-llms-the-power-of-bm25-and-rrf-dd76ed75e4e3)
[^266]: [From Search to Synthesis: Enhancing RAG with BM25 and ... - Medium](https://medium.com/@kachari.bikram42/from-search-to-synthesis-enhancing-rag-with-bm25-and-reciprocal-rank-fusion-872d21dc4ca7)
[^267]: [Hybrid retrieval - BM25 with multilingual RAG - Reddit](https://www.reddit.com/r/Rag/comments/1gdfcsr/hybrid_retrieval_bm25_with_multilingual_rag/)
[^271]: [Understanding Okapi BM25: A Guide to Modern ...](https://adasci.org/understanding-okapi-bm25-a-guide-to-modern-information-retrieval/)
[^272]: [New graph-RAG technique boost LLMs in multi-hop ...](https://bdtechtalks.substack.com/p/new-graph-rag-technique-boost-llms)
[^273]: [From Basic to Advanced RAG every step of the way](https://rahuld3eora.medium.com/from-basic-to-advanced-rag-every-step-of-the-way-dee3a3a1aae9)
[^277]: [An Enhanced Retrieval Scheme for a Large Language Model with a ...](https://www.mdpi.com/2076-3417/14/24/11529)
[^285]: [Top 9 RAG Tools to Boost Your LLM Workflows](https://lakefs.io/blog/rag-tools/)
[^289]: [Introduction to Elasticsearch similarity scoring model - Medium](https://medium.com/@dongliang0828/introduction-to-elasticsearch-similarity-scoring-model-47d485fa7490)
[^290]: [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
[^291]: [What is BM25 (Best Matching 25) Algorithm? - GeeksforGeeks](https://www.geeksforgeeks.org/what-is-bm25-best-matching-25-algorithm/)
[^295]: [Understanding Okapi BM25: A Guide to Modern Information Retrieval](https://adasci.org/understanding-okapi-bm25-a-guide-to-modern-information-retrieval/)
[^296]: [Mastering BM25: A Deep Dive into the Algorithm and Its Application ...](https://zilliz.com/learn/mastering-bm25-a-deep-dive-into-the-algorithm-and-application-in-milvus)
[^297]: [What is BM25 (Best Matching 25) Algorithm? - GeeksforGeeks](https://www.geeksforgeeks.org/nlp/what-is-bm25-best-matching-25-algorithm/)
[^307]: [What is BM25? - Online Marketing Consulting](https://www.kopp-online-marketing.com/what-is-bm25)
[^313]: [BM25 for Python: Achieving high performance while simplifying ...](https://huggingface.co/blog/xhluca/bm25s)
[^314]: [Optimizing BM25 for the Next Generation of Semantic Search ... - Exa](https://exa.ai/blog/bm25-optimization)