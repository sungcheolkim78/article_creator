# BM25: An Advanced Ranking Algorithm for Document Retrieval Systems

## BM25 및 문서 검색 소개

### BM25 정의: Best Matching 25
BM25는 Best Matching 25의 약어로, Okapi BM25라고도 불리며 정보 검색 분야에서 근본적이고 널리 채택되는 점수화 및 순위 지정 알고리즘입니다. 확률 모델로 작동하며, 주요 기능은 문서가 주어진 검색 쿼리와 일치하는 정도를 평가하여 문서의 관련성을 추정하는 것입니다 [^4], [^10]. 이 강력한 방법은 문서 내 용어의 빈도(용어 빈도), 문서의 전체 길이, 쿼리 용어의 역문서 빈도(IDF) 등 여러 요소를 복합적으로 고려하여 관련성 점수를 계산합니다 [^5], [^11], [^17]. 단순한 접근 방식과 달리 BM25는 일반적으로 *k1*(일반적으로 1.2에서 2.0 사이로 설정) 및 *b*(일반적으로 0.75)와 같은 자유 매개변수를 통합하여 계산을 미세 조정하고 용어 빈도 포화 및 문서 길이 정규화와 같은 측면을 제어할 수 있습니다 [^12], [^18], [^64].

### 정보 검색 및 검색 엔진에서의 역할
Okapi BM25는 정교한 순위 함수로서 현대 정보 검색 시스템과 검색 엔진에서 중요한 역할을 합니다. 그 핵심 유용성은 사용자의 특정 검색 쿼리에 대한 방대한 수의 문서의 관련성을 효과적으로 추정하고 결정하는 능력에 있습니다 [^10], [^16]. BM25는 용어 빈도, 문서 빈도 및 문서 길이의 영향을 균형 있게 조절하여 긴 문서가 실제 관련성 없이 본질적으로 과도한 점수를 받지 않도록 보장하는 데 중요합니다 [^17], [^190]. 이 균형 잡힌 접근 방식은 고급 점수화 방법으로 BM25를 구별합니다. 전통적인 검색을 넘어, BM25는 Azure AI Search의 키워드 검색과 같은 현대 시스템에 점점 더 통합되고 있으며 [^18], 검색 및 검색 성능을 향상시키기 위해 대규모 언어 모델(LLM)과 결합되어 Retrieval-Augmented Generation(RAG)과 같은 애플리케이션에 활용됩니다 [^4], [^265]. 또한 BM25는 속도와 정밀도 덕분에 BM25와 FAISS를 결합한 하이브리드 검색 아키텍처에서 초기 필터 역할을 할 수 있습니다 [^235], [^249].

### 순위 알고리즘의 진화
BM25는 TF-IDF(용어 빈도-역문서 빈도)와 같은 이전 모델을 기반으로 개선하여 문서 순위 알고리즘 분야에서 중요한 진화를 의미합니다 [^5], [^28]. TF-IDF는 용어의 빈도와 희귀성에 따라 가중치를 부여하는 간단한 방법을 제공하지만, BM25는 더 발전되고 미세 조정된 메커니즘을 도입합니다 [^29]. 주요 개선 사항으로는 과도하게 높은 용어 빈도가 문서 점수를 불균형하게 부풀리는 것을 방지하는 용어 빈도 포화에 대한 정교한 처리가 포함됩니다 [^208], [^211]. 또한 BM25는 문서의 길이가 관련성 점수에 지나치게 영향을 미치지 않도록 하는 강력한 문서 길이 정규화 메커니즘을 통합하는데, 이는 더 간단한 모델에서 종종 관찰되는 한계입니다 [^17], [^196]. 이러한 개선 사항은 BM25가 이전 모델보다 더 강력하고 효과적이며 미묘한 순위 알고리즘으로 간주되는 데 기여하며, 정확하고 상세한 검색 결과를 얻기 위한 선호되는 선택이 됩니다 [^30], [^307].

## BM25의 작동 방식 이해하기

### 확률 모델 및 관련성 점수화
Okapi BM25는 Best Matching 25라고도 불리며, 정보 검색 시스템에서 널리 사용되는 점수화 및 순위 지정 알고리즘입니다. 이는 확률 모델로 작동하며, 주요 기능은 문서가 주어진 검색 쿼리와 얼마나 효과적으로 일치하는지 평가하여 문서의 관련성을 추정하는 것입니다. TF-IDF와 같은 이전 모델의 진화형인 BM25는 용어 빈도, 문서 길이, 역문서 빈도(IDF)와 같은 요소를 통합하여 정확한 관련성 점수를 계산함으로써 내재된 몇 가지 한계를 해결합니다 [^4], [^10]. BM25는 이러한 요소를 균형 있게 조정하고 특히 문서 길이를 정규화하여 단순히 길이 때문에 더 긴 문서가 불균형적으로 높은 점수를 받지 않도록 하는 강력한 점수화 방법으로 설계되었습니다 [^16]. 이 모델은 또한 TF-IDF와 같은 더 간단한 접근 방식과 차별화되는 빈도 포화(frequency saturation)를 통합합니다 [^16], [^208].

### BM25 수학 공식
Okapi BM25 순위 함수는 검색 엔진에서 문서와 주어진 쿼리의 관련성을 추정하는 데 사용되며, 용어 빈도 포화 및 문서 길이를 고려하여 TF-IDF의 기능을 확장합니다. 키워드 q1부터 qn을 포함하는 쿼리 Q가 주어졌을 때, 문서 D의 BM25 점수는 다음 공식을 사용하여 계산됩니다 [^118]:

${\displaystyle {\text{score}}(D,Q)=\sum _{i=1}^{n}{\text{IDF}}(q_{i})\cdot {\frac {f(q_{i},D)\cdot (k_{1}+1)}{f(q_{i},D)+k_{1}\cdot \left(1-b+b\cdot {\frac {|D|}{\text{avgdl}}}\right)}}}$

이 공식은 문서 관련성에 대한 미묘한 평가를 가능하게 하며, 강력한 순위 지정 기능을 달성하기 위해 여러 중요한 구성 요소와 자유 매개변수를 고려합니다 [^70], [^118].

### 공식의 구성 요소: f(qi,D), |D|, avgdl, IDF(qi)
BM25 공식 내에서 몇 가지 주요 구성 요소는 관련성 점수를 계산하는 데 중요합니다. $f(q_i, D)$는 용어 빈도를 나타내며, 쿼리 용어 $q_i$가 문서 D 내에 몇 번 나타나는지를 나타냅니다 [^64], [^118]. $|D|$는 문서 D의 길이를 의미하며, 일반적으로 단어 수로 측정됩니다. 반면 $avgdl$은 검색되는 문서 전체 코퍼스의 평균 문서 길이를 나타냅니다 [^118]. $IDF(q_i)$는 쿼리 용어 $q_i$에 대한 역문서 빈도(Inverse Document Frequency) 가중치로, 코퍼스 전체에서 해당 용어의 희귀성을 반영합니다. 더 적은 문서에 나타나는 용어는 일반적으로 더 높은 IDF 가중치를 가집니다 [^64], [^76], [^118]. 또한, 이 공식에는 두 개의 자유 매개변수 $k_1$과 $b$가 포함됩니다. 매개변수 $k_1$은 용어 빈도 포화를 제어하며, 일반적으로 1.2에서 2.0 사이입니다. $k_1$ 값이 높을수록 포화되기 전에 용어의 여러 출현이 점수에 더 크게 기여할 수 있습니다 [^64], [^76], [^166]. 매개변수 $b$는 문서 길이 정규화의 영향을 결정하며, 일반적으로 0.75로 설정됩니다. $b$ 값이 0이면 길이 정규화가 없음을 의미하며, 1이면 완전한 정규화를 의미하여 단순히 길이 때문에 더 긴 문서가 불공정한 이점을 얻는 것을 방지합니다 [^64], [^76], [^184], [^196].

### 확률 모델(예: 이진 독립 모델)로부터의 파생
Okapi BM25는 확률적 정보 검색 모델 계열에 뿌리를 두고 있으며, 특히 이진 독립 모델(Binary Independence Model, BIM)로부터 그 기반을 파생합니다 [^10], [^40], [^58]. BM25 공식의 중요한 부분인 역문서 빈도(IDF) 구성 요소는 BIM에서 직접 파생됩니다 [^34], [^40]. BIM이 문서 관련성을 평가하기 위한 개념적 프레임워크 역할을 하지만, BM25는 이 모델을 크게 확장합니다. BM25는 기본적인 BIM에는 없는 문서 내 용어 빈도 정보, 문서 길이 정규화, 추가적인 문서 및 쿼리 용어 가중치를 통합합니다 [^46]. BM25의 설계는 $k_1$ 및 $b$와 같은 자유 매개변수를 포함하여, 적절하게 조정될 경우 BIM 모델에 더 가깝게 근사할 수 있도록 합니다 [^52]. 이러한 강력한 파생은 BM25가 순위 지정 알고리즘으로서 효과적인 기반이 됩니다 [^58].

## 주요 매개변수 및 그 영향

문서 순위 지정에서 BM25 알고리즘의 효과는 `k1`과 `b`라는 두 가지 중요한 자유 매개변수에 크게 좌우됩니다. 이 매개변수는 알고리즘의 동작을 특정 코퍼스와 검색 요구 사항에 맞게 미세 조정하여 용어 빈도와 문서 길이가 문서의 관련성 점수에 기여하는 방식에 영향을 미칩니다 [^10][^16][^22][^64][^70][^76][^82][^118].

### k1 매개변수: 용어 빈도 포화 및 비선형 가중치

BM25의 `k1` 매개변수는 용어 빈도 포화를 제어하고 문서 내 용어의 비선형 가중치를 구현하는 데 핵심적인 역할을 합니다. 이는 쿼리 용어가 문서 내에 더 자주 나타남에 따라 문서의 관련성 점수가 얼마나 빨리 증가하는지를 결정합니다 [^166][^211][^229]. 모든 용어 출현에 따라 점수를 선형적으로 증가시킬 수 있는 단순한 모델과 달리, BM25는 `k1`을 통해 비선형 접근 방식을 사용하여 과도하게 높은 용어 빈도가 문서 점수를 불균형하게 부풀리는 것을 방지합니다 [^208][^217][^223]. `k1` 값이 높을수록 용어 빈도가 "포화"되거나 평준화되기 전까지 더 오랫동안 점수에 더 크게 기여할 수 있습니다. 반대로, `k1`이 0으로 설정되면 용어 빈도는 영향을 미치지 않으며, 검색 용어의 역문서 빈도(IDF)만이 점수에 기여합니다 [^154]. 이 메커니즘은 관련성 점수에 대한 균형 있고 미묘한 접근 방식을 보장하여 BM25를 TF-IDF와 같은 덜 정교한 방법과 차별화합니다 [^28][^208].

### b 매개변수: 문서 길이 정규화

`b` 매개변수는 BM25 점수 함수 내에서 문서 길이 정규화에 매우 중요합니다. 주요 역할은 문서 길이에 따라 점수를 조정하여 긴 문서가 단순히 더 많은 용어를 포함한다는 이유만으로 본질적으로 더 높은 관련성 점수를 받는 것을 방지하는 것입니다 [^190][^202]. 이 메커니즘은 긴 문서를 의도치 않게 선호할 수 있는 TF-IDF와 같은 단순한 모델과 BM25를 구별하는 핵심 요소입니다 [^28][^196]. `b` 매개변수는 이 정규화의 정도를 0에서 1까지 제어합니다. `b`가 0으로 설정되면 문서 길이 정규화가 적용되지 않으므로 문서 길이가 점수에 영향을 미치지 않습니다 [^106][^196]. 반대로, `b`가 1로 설정되면 문서의 용어 빈도 구성 요소가 길이에 따라 완전히 정규화됩니다 [^184][^196]. `b` 값이 높을수록 긴 문서에 대한 패널티가 커지며, 이는 짧은 문서와 동일한 관련성 점수를 얻기 위해 용어 빈도가 약간 더 높아야 함을 의미합니다 [^184]. 이를 통해 다양한 길이의 문서 전반에 걸쳐 공정한 관련성 점수 산정이 보장됩니다 [^178][^192].

### k1 및 b에 대한 경험적 근거 및 튜닝 지침

`k1` 및 `b` 매개변수는 BM25 점수 함수 내의 자유 매개변수이며, 일반적으로 경험적 관찰 및 데이터셋 특성을 기반으로 선택됩니다 [^10][^64][^70][^76][^82][^118]. BM25의 IDF 구성 요소는 이진 독립 모델(BIM)에 뿌리를 두고 있지만, 전체 BM25 모델은 용어 빈도, 문서 길이 정규화 및 추가 용어 가중치를 통합하여 BIM을 확장하며, `k1`과 `b`는 모델이 BIM을 더 가깝게 근사하도록 합니다 [^40][^46][^52].

`k1`의 일반적인 값은 1.2에서 2.0 범위에서 흔히 관찰되며, `b`는 자주 0.75로 설정됩니다 [^10][^16][^22][^64][^70][^76][^82][^100][^106][^118]. 예를 들어, 아파치 루씬(Apache Lucene)은 특히 `k1 = 1.2`와 `b = 0.75`를 사용합니다 [^100]. 그러나 이 매개변수의 최적 값은 사용되는 특정 데이터 컬렉션 또는 코퍼스에 따라 크게 달라집니다 [^172]. 전용 매개변수 튜닝이 수행될 수 있지만(예를 들어, 엘라스틱서치(Elasticsearch)는 0에서 3 사이의 `k1` 값을 탐색했습니다 [^148]), 검색 시스템에서 관련성을 최적화하기 위한 초기 노력은 보다 표현력이 풍부한 쿼리 언어, 언어 제어 및 사용자 피드백 통합에 더 잘 할애되는 경우가 많습니다. `k1`과 `b`를 깊이 조정하는 것은 이러한 더 광범위한 관련성 기능이 처리된 후에 고려될 수 있습니다 [^148][^172].

## BM25 vs. TF-IDF: 랭킹 알고리즘의 진화

### TF-IDF: 선행자
TF-IDF(Term Frequency-Inverse Document Frequency)는 정보 검색의 기초적인 방법으로, 주로 문서 내 단어의 빈도와 전체 코퍼스에서의 희귀도를 기반으로 단어의 가중치를 부여하는 데 사용됩니다. 이는 문서 집합 내에서 특정 단어가 문서에 얼마나 중요한지를 평가하는 간단하면서도 효과적인 접근 방식을 제공합니다 [^28]. 이 방법은 각 용어에 대한 점수를 계산하는데, 문서에 얼마나 자주 나타나는지(단어 빈도)와 모든 문서에서 얼마나 고유한지(역문서 빈도)를 고려하여, 너무 흔하지 않으면서 특정 문서에 중요한 용어를 식별합니다 [^28].

### TF-IDF의 한계점 해결
TF-IDF가 중요한 기반을 마련했지만, Okapi BM25라고도 불리는 BM25(Best Matching 25)는 랭킹 알고리즘에서 중요한 진화와 개선으로 등장했습니다 [^5], [^28]. 확률 모델로서 BM25는 TF-IDF와 같은 더 단순한 선행 방법의 내재된 여러 한계를 해결합니다 [^5], [^10]. 특히, BM25는 TF-IDF가 완전히 고려하지 못하는 문서 길이 정규화 및 정교한 용어 빈도 처리와 같은 고급 고려 사항을 도입합니다 [^16], [^28]. 이를 통해 BM25는 문서 관련성에 대한 더 미묘하고 정확한 평가를 제공할 수 있습니다 [^28].

### 빈도 포화와 그 중요성
BM25의 주요 차별점은 TF-IDF와 같은 단순한 방법에는 없는 빈도 포화를 고려한다는 것입니다 [^16], [^208]. 빈도 포화는 문서 내에서 용어의 빈도가 특정 지점을 초과하여 증가할수록 용어의 관련성 점수에서 얻는 이득이 감소하는 것을 의미합니다 [^166]. BM25는 이 포화를 관리하기 위해 `k1` 매개변수로 제어되는 비선형 용어 빈도 가중치를 통합합니다 [^223], [^229]. 일반적으로 1.2에서 2.0 사이로 설정되는 `k1` 매개변수는 용어 빈도가 증가함에 따라 관련성 점수가 얼마나 빨리 평준화되는지를 결정하여, 과도하게 높은 용어 수가 문서의 점수를 불균형하게 부풀리는 것을 방지합니다 [^100], [^166], [^208]. 이 메커니즘은 용어 빈도가 전체 관련성 점수에 보다 균형 있고 현실적인 기여를 하도록 보장합니다 [^229].

### 문서 관련성의 우월성
전반적으로 BM25는 TF-IDF보다 더 강력하고 효과적인 랭킹 알고리즘으로 널리 인정받고 있으며, 현대 검색 엔진에서 상세하고 정확한 결과를 얻기 위한 선호되는 선택입니다 [^28], [^208]. 그 우월성은 용어 빈도, 문서 길이, 그리고 중요한 빈도 포화 요소 등 다양한 요소를 보다 효과적으로 균형 있게 맞추는 능력에서 비롯됩니다 [^16], [^295]. 문서 길이를 정규화함으로써 BM25는 단순히 길이가 길다는 이유로 긴 문서가 더 높은 점수를 받지 않도록 보장하며, 실제로 더 관련성이 있는 경우에만 높은 점수를 받습니다 [^28], [^190]. 이 포괄적인 접근 방식은 BM25가 문서 관련성을 추정하는 세밀한 방법을 제공하여, TF-IDF의 기본적인 가중치 부여 방식에 비해 상당한 발전을 이룩했음을 보여줍니다 [^28].

## BM25의 실제 적용 및 구현

### 독립형 재순위 지정 및 속도 고려 사항
Okapi BM25는 Best Matching 25로도 알려져 있으며, 정보 검색 시스템에서 견고하고 널리 사용되는 순위 함수로, 독립형 문서 재순위 지정기로 효과적으로 배포될 수 있습니다 [^22, ^253]. BERT 기반 점수 매기기와 같이 계산 집약적인 모델과 비교할 때, BM25는 작업 완료에 몇 분이 아닌 몇 초가 걸리는 상당한 속도 이점을 제공합니다 [^22]. 이러한 효율성은 부분적으로 O(n)의 계산 복잡성에 기인하며, 이는 다른 관련성 점수 모델과 일치합니다 [^289, ^301]. BM25의 설계는 용어 빈도, 문서 길이, 역문서 빈도와 같은 요소를 계산 효율성을 유지하면서 균형을 맞출 수 있도록 합니다 [^307]. 자유 매개변수인 `k1`과 `b`는 특정 데이터 컬렉션에 맞게 조정될 수 있지만, 초기 최적화 노력은 표현력 있는 쿼리 언어 또는 언어 제어와 같은 다른 관련성 기능에 집중할 때 더 큰 효과를 낼 수 있습니다 [^148, ^172]. 또한 BM25는 문서와 쿼리를 희소 벡터로 변환하여 벡터 데이터베이스에 효율적인 저장 및 검색을 용이하게 합니다 [^295, ^313].

### 벡터 데이터베이스(예: FAISS)를 사용한 하이브리드 검색
문서 검색을 향상시키고 검색 증강 생성(RAG) 시스템 성능을 개선하기 위해 BM25는 FAISS와 같은 벡터 데이터베이스와 하이브리드 검색 아키텍처에서 자주 결합됩니다 [^235, ^247]. 이 접근 방식은 BM25의 정확한 키워드 기반 검색 강점을 활용하며, 종종 초기 필터로 사용하여 결과를 좁힙니다. 이어서 FAISS는 밀집 검색 방법을 통해 맥락적 관계를 포착하는 의미론적 정교화를 적용합니다 [^235, ^247, ^253]. 워크플로우는 일반적으로 문서 인덱싱을 포함하며, 그 다음 BM25가 초기 키워드 기반 검색을 수행합니다. FAISS는 의미론적 관계를 포착하기 위해 검색을 수행하며, 두 결과는 병합되어 관련성이 높은 문서를 제공합니다 [^259]. 이러한 통합은 효율성과 관련성을 극대화하고 전통적인 키워드 이해와 맥락적 이해를 연결하는 강력한 시스템을 형성합니다 [^241, ^247]. 이러한 서로 다른 구성 요소를 결합하기 위해 "EnsembleRetriever"를 활용할 수 있습니다 [^241].

### RAG 시스템에서 대규모 언어 모델(LLM)과의 통합
BM25는 대규모 언어 모델(LLM)을 활용하는 검색 증강 생성(RAG) 시스템 내에서 검색 단계의 향상에 중요한 역할을 합니다 [^4, ^265, ^271]. 효율적인 용어 기반 순위 모델로서 BM25는 사용자 쿼리를 기반으로 데이터 소스에서 관련 구절 또는 문서 세트를 검색하는 데 사용됩니다 [^271, ^277]. RAG 파이프라인에서 BM25 검색 결과는 종종 벡터 데이터베이스 검색 결과와 결합되며, Reciprocal Rank Fusion(RRF)과 같은 방법을 활용하여 여러 검색 기술의 점수를 통합하고 전체 검색 성능을 향상시킵니다 [^265, ^277, ^283]. 이러한 관련 구절이 검색되면 LLM은 이를 처리하여 의미론적 이해, 요약 및 사용자 쿼리에 대한 포괄적이고 맥락적으로 관련된 답변을 생성합니다 [^271, ^283]. 효율적인 키워드 기반 검색을 위한 BM25와 고급 의미론적 처리를 위한 LLM의 이러한 조합은 RAG 시스템이 크고 동적인 데이터셋을 효과적으로 처리함으로써 순수 LLM의 한계를 극복하고 전반적인 검색 및 검색 기능을 향상시킬 수 있도록 합니다 [^271, ^295].

## BM25의 성능 및 확장성

### 계산 복잡성 및 효율성
BM25는 다른 관련성 점수 모델과 유사하게 O(n)의 계산 복잡성을 보입니다 [^289, ^290, ^291]. 이러한 효율성은 특히 BERT 기반 점수화와 같이 계산 집약적인 방법과 비교할 때 핵심적인 특징입니다. BM25는 재순위 지정 작업에서 BERT 기반 방법이 몇 분이 걸리는 반면, 몇 초 안에 작동할 수 있어 훨씬 빠릅니다 [^22, ^23, ^24]. TF-IDF와 같은 초기 모델의 진화형인 BM25는 용어 빈도, 문서 빈도 및 문서 길이를 포함한 요소를 효과적으로 균형을 맞춰 관련성 점수화를 개선하면서 계산 효율성을 유지합니다 [^295, ^296, ^297, ^301, ^302, ^303, ^307, ^308, ^309]. 견고한 설계 덕분에 긴 문서가 순위에서 과도하게 지배하는 것을 방지하기 위해 점수를 정규화함으로써 검색 결과를 향상시킬 수 있습니다 [^295, ^296, ^297].

### 인덱싱 전략 (예: 역색인 목록)
BM25의 확장성과 성능은 기본 데이터 구조 및 구현 전략과 본질적으로 연결되어 있습니다. 이 알고리즘은 일반적으로 효율적인 문서 검색을 용이하게 하는 인메모리 역색인 목록 데이터 구조에 의존합니다 [^313, ^314, ^315]. 독립형 구현 외에도 BM25는 FAISS와 결합하는 것과 같은 하이브리드 검색 아키텍처에서 중요한 역할을 합니다. 이러한 시스템에서 BM25는 종종 정확한 키워드 기반 검색을 위한 초기 필터 역할을 하여, FAISS와 같은 밀집 검색 방법이 의미론적 정제를 적용하기 전에 결과를 좁힙니다 [^22, ^23, ^24, ^235, ^236, ^237, ^247, ^248, ^249, ^259, ^260, ^261]. 정확한 키워드 일치에 중점을 둔 이러한 "희소(sparse)" 검색 기능은 의미론적 이해를 위해 벡터 임베딩을 사용하는 "밀집(dense)" 검색 기술을 보완합니다 [^241, ^242, ^243]. 이 프로세스는 일반적으로 문서 인덱싱, 두 구성 요소를 사용한 검색 수행, 그리고 효율성과 관련성을 모두 극대화하기 위해 결과를 병합하는 과정을 포함합니다 [^235, ^236, ^237]. 또한, BM25는 문서와 쿼리를 희소 벡터로 변환하는 데 사용될 수 있으며, 이는 Milvus와 같은 확장 가능한 벡터 데이터베이스에 효율적으로 저장하고 검색할 수 있습니다 [^295, ^296, ^297, ^313, ^314, ^315].

### 메모리 고려사항
메모리 사용량은 BM25의 확장성에 중요한 요소이며, 특히 인메모리 역색인 목록 데이터 구조에 대한 의존성을 고려할 때 더욱 그렇습니다 [^313, ^314, ^315]. BM25 구현의 효율성은 메모리 오버헤드와 포스팅 목록에 대한 `malloc` 호출과 같은 메모리 할당 요청과 관련된 압력에 의해 영향을 받을 수 있습니다 [^313, ^314, ^315]. 확장성 및 메모리 문제를 해결하기 위해 BM25는 문서와 쿼리를 희소 벡터로 표현하도록 조정될 수 있습니다. 이 접근 방식은 Milvus와 같은 벡터 데이터베이스 내에 효율적으로 저장하고 검색할 수 있도록 하여 대규모 데이터셋 전반의 작업을 용이하게 합니다 [^295, ^296, ^297, ^313, ^314, ^315].

## 한계 및 향후 방향

### 본질적인 한계 (예: 의미 이해)
TF-IDF의 진화이자 이진 독립 모델(Binary Independence Model)에서 파생된 확률 모델인 BM25는 용어 빈도, 문서 길이, 역문서 빈도와 같은 요소를 균형 있게 조절하여 관련성을 추정함으로써 키워드 기반 검색에서 탁월한 성능을 발휘합니다 [^4], [^16], [^34], [^40]. 그러나 정확한 키워드 일치에 강점이 있다는 점은 본질적인 한계, 즉 의미 이해의 부족을 부각시킵니다. BM25는 주로 용어의 통계적 출현과 분포를 기반으로 문서를 평가하므로 단어 간의 더 깊은 의미, 맥락 또는 의미 관계를 본질적으로 파악하지 못합니다 [^241], [^271]. 이는 동의어, 다의어 또는 질의 의도가 키워드를 통해 명시적으로 표현되지 않은 시나리오에서 어려움을 초래할 수 있습니다. 즉, 문맥적으로 관련성이 높지만 정확한 질의 용어를 포함하지 않는 문서를 검색하는 데 어려움을 겪습니다 [^241]. 용어 가중치 및 길이 정규화에는 강력하지만, 그 기반은 의미론적 모델이 제공하는 미묘한 언어 이해까지 확장되지 않습니다 [^16], [^217].

### 한계 극복 및 향후 개선 사항
특히 의미 이해와 관련된 본질적인 한계를 극복하기 위해 BM25는 점점 더 고급 및 하이브리드 검색 아키텍처에 통합되고 있습니다. 한 가지 중요한 접근 방식은 BM25를 FAISS와 같은 밀집 검색(dense retrieval) 방법과 결합하여 하이브리드 검색 시스템을 구축하는 것입니다 [^23], [^235]. 이러한 파이프라인에서 BM25는 종종 효율적인 초기 필터 역할을 하여 정확한 키워드 일치를 기반으로 결과를 좁히고, FAISS는 벡터 임베딩을 사용하여 의미론적 개선을 적용하여 문맥적 관계를 파악합니다 [^23], [^247], [^253]. 이 조직화된 워크플로는 일반적으로 문서를 인덱싱하고, 두 가지 방법으로 검색을 수행한 다음, 결과를 병합하여 키워드 정확성과 의미 이해 모두에서 이점을 얻는 고도로 관련성 있는 문서를 제공합니다 [^235], [^259].

또한 BM25는 대규모 언어 모델(LLM)을 활용하는 검색 증강 생성(RAG) 시스템에서 중요한 역할을 합니다 [^4], [^295]. 이 아키텍처에서 BM25는 사용자 질의를 기반으로 관련 구절 또는 문서 세트를 효율적으로 검색합니다 [^271]. 이렇게 검색된 구절은 LLM에 전달되어 의미 이해, 요약 및 포괄적이고 문맥적으로 관련성 있는 답변 생성을 위해 처리됩니다 [^271], [^277], [^283]. 이러한 시너지는 LLM이 검색된 정보에 생성 능력을 기반을 두어 방대한 동적 데이터셋을 처리할 수 있도록 하며, BM25의 의미론적 이해 한계를 효과적으로 해결합니다 [^271]. 상호 순위 융합(RRF)과 같은 방법은 BM25 및 벡터 데이터베이스 검색을 포함한 여러 검색 방법의 점수를 지능적으로 결합하여 검색 성능을 향상시키는 데에도 사용됩니다 [^265], [^277]. 시스템 통합 외에도, BM25의 자유 매개변수인 `k1`(용어 빈도 포화도 제어) 및 `b`(문서 길이 정규화 제어)를 지속적으로 최적화하면 특정 데이터 컬렉션에 대한 성능을 미세 조정할 수 있지만, 더 광범위한 관련성 기능이 더 실질적인 이득을 제공할 수 있습니다 [^148], [^172], [^196]. BM25의 계산 효율성과 확장성은 복잡하고 고성능 정보 검색 시스템의 핵심 구성 요소로서 지속적인 관련성을 보장합니다 [^289], [^307], [^313].

## 결론

### BM25의 영향 요약
BM25, 즉 Best Matching 25는 정보 검색 분야의 초석으로 자리 잡고 있으며, 검색 엔진에서 주어진 쿼리에 대한 문서 관련성을 측정하기 위해 널리 채택되는 정교한 확률 모델로 기능합니다 [^4], [^10]. 이 알고리즘은 TF-IDF와 같은 더 간단한 용어 가중치 방식에서 중요한 발전을 나타내며, 용어 빈도 포화 및 강력한 문서 길이 정규화와 같은 고급 요소를 통합하여 기존 방식의 한계를 체계적으로 해결합니다 [^28], [^29], [^30]. BM25의 수학적 기초는 Binary Independence Model(BIM)에 뿌리를 두고 있으며, 이는 역문서 빈도(IDF) 구성 요소에 정보를 제공하면서 문서 내 용어 빈도 정보 및 문서 길이 조정을 통합하도록 확장합니다 [^34], [^40], [^46].

BM25의 주요 강점은 용어 빈도 기여도와 문서 길이 정규화를 각각 제어하는 신중하게 균형 잡힌 매개변수, 특히 `k1`(일반적으로 1.2-2.0)과 `b`(일반적으로 0.75)에 있습니다 [^64], [^70], [^76]. `k1` 매개변수는 용어가 더 자주 나타날수록 관련성 점수가 얼마나 빨리 포화되는지를 결정하여 과도하게 반복되는 용어로 인한 불필요한 가중치를 방지합니다 [^166], [^208]. 동시에 `b` 매개변수는 긴 문서가 본질적으로 선호되지 않도록 보장하며, 코퍼스 내 평균 문서 길이에 상대적으로 점수를 정규화합니다 [^178], [^190], [^196]. 이러한 미묘한 접근 방식은 BM25를 강력하고 효과적인 순위 지정 알고리즘으로 확고히 했으며, 정확한 검색 결과 제공에서 더 간단한 방법보다 지속적으로 우수한 성능을 보입니다 [^28], [^30]. 또한 BM25는 계산 효율성을 유지하며 O(n)의 복잡성을 보여 대규모 문서 검색 시스템에 매우 실용적입니다 [^289], [^301], [^307].

### 문서 검색의 미래 방향
BM25의 지속적인 관련성은 특히 인공지능 발전과 더불어 최첨단 문서 검색 시스템에 지속적으로 통합되는 데서 분명히 드러납니다. 중요한 방향은 Retrieval-Augmented Generation(RAG) 아키텍처에서 대규모 언어 모델(LLM)과의 결합을 포함합니다 [^4], [^265]. 이러한 파이프라인에서 BM25는 일반적으로 키워드 일치를 기반으로 관련 구절 또는 문서를 식별하는 효율적인 초기 검색기로 작동합니다. 검색된 결과는 LLM에 공급되어, LLM은 더 깊은 의미 이해, 요약 및 포괄적이고 상황에 맞는 답변 생성을 위해 정보를 처리합니다 [^271], [^272], [^273].

RAG 외에도 BM25는 기존 키워드 기반 검색과 현대적인 의미 검색을 병합하는 하이브리드 검색 시스템에서 중요한 구성 요소입니다. 예를 들어, BM25-FAISS 하이브리드 아키텍처에서 BM25는 FAISS가 벡터 임베딩을 통해 의미론적 정제를 적용하기 전에 키워드를 기반으로 결과를 정확하게 좁히는 초기 필터 역할을 합니다 [^235], [^247], [^253]. 이 조합은 정확한 일치에 대한 BM25의 정확성과 문맥적 관계를 포착하는 FAISS의 능력을 활용하여, 더 강력하고 미묘한 검색 시스템을 만듭니다 [^253], [^259]. Reciprocal Rank Fusion(RRF)과 같은 기술도 BM25와 벡터 데이터베이스 검색의 점수를 효과적으로 결합하여 검색 성능을 더욱 향상시키는 데 사용됩니다 [^265], [^277], [^283]. 정보의 양과 복잡성이 계속 증가함에 따라 BM25의 적응성, 계산 효율성 및 강력한 순위 지정 기능은 지능형 정보 검색 및 생성 AI 애플리케이션의 발전하는 환경에서 그 기반 역할을 보장합니다.

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