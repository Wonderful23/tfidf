
import math
import os.path
class Graph(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.articleNodes = []  ##
        self.wordCountNodes = dict()  ## 统计词的总数
        self.wordArticleNodes = dict()  ## 统计词的篇数
        self.articleTFIDF = []
        self.wordIndex = dict()
        self.articleVector = []
        self.similarityMatrix = []
        self.articleIndex = []
        ## 设置关注的词的词性
        self.pos = {'n', 'x', 'eng', 'f', 's', 't', 'nr', 'ns',
                    'nt', 'nw', 'nz', 'PER', 'LOC', "ORG", "TIME",
                    'a', 'i', 'v', 'l', 'vn', 'vl', 'vg', 'ag', 'al', 'an', 'ad'}
        # 导入停用词
        file = open('stoplist.txt', 'r', encoding="utf-8")
        self.stoplist = file.read().split('\n')
        file.close()

    ### 第一步首先构建图的全局词视图,计算满足条件的词在单篇新闻中的词频并统计单个单词出现的篇数,以及词在全文的总数
    def calculateWords(self):
        file = open(self.filepath, 'r', encoding='gbk')
        lines = []
        line = file.readline()
        lines.append(line)
        articleName = line[0:15]
        self.articleIndex.append(articleName)
        for line in file:
            words = line.split('  ')  ## 注意分词是双空格
            if len(words) <= 1:
                continue
            tempWords = words[0].split('/')
            if len(tempWords[0]) != 19:
                lines.append(line)
            else:
                tempName = tempWords[0][0:15]
                if tempName == articleName:
                    lines.append(line)
                else:
                    self.articlecalculatehelper(lines)
                    lines.clear()
                    lines.append(line)
                    articleName = tempName
                    self.articleIndex.append(articleName)
        if len(lines) != 0:
            self.articlecalculatehelper(lines)
        file.close()

    ### 统计词频辅助函数
    def articlecalculatehelper(self, lines):
        articleWords = dict()
        for line in lines:
            words = line.split('  ')  ## 注意分词是双空格
            for word in words:
                tempWords = word.split('/')
                if len(tempWords) != 2:
                    continue
                if len(tempWords[0]) == 1 or tempWords[0] in self.stoplist:
                    continue
                if tempWords[1] in self.pos:
                    # 记录单词出现的篇数
                    num = self.wordCountNodes.get(tempWords[0], 0)
                    self.wordCountNodes[tempWords[0]] = num + 1
                    # 记录单词在这篇文章出现的频率
                    num = articleWords.get(tempWords[0], 0)
                    articleWords[tempWords[0]] = num + 1
        for word, value in articleWords.items():
            num = self.wordArticleNodes.get(word, 0)
            self.wordArticleNodes[word] = num + 1
        self.articleNodes.append(articleWords)

    ## 计算TFIDF的值，并标准化，去除尾部数据
    def calculateTFIDF(self):
        articleSum = len(self.articleNodes)
        for article in self.articleNodes:
            tempArticle = dict()
            for word, value in article.items():
                sum = self.wordCountNodes.get(word, 0)
                types = self.wordArticleNodes.get(word, 0)
                Tf_Idf = value / float(sum) * math.log1p(articleSum / (types+1))
                tempArticle[word] = Tf_Idf
            tempArticle = self.normalize(tempArticle)
            self.articleTFIDF.append(tempArticle)
        # print(self.articleTFIDF)

    def normalize(self, article):
        sum = 0
        sum1 = 0
        n = len(article)
        newArticle = dict()
        for word, value in article.items():
            sum += value
            sum1 += value * value
        means = sum / n
        var = math.sqrt((sum1 - n * means * means) / (n - 1))
        cut = -var
        for word, value in article.items():

            if var < 0.000001:
                newValue = 0
            else:
                newValue = (value - means) / var
            if newValue < cut and var != 0:
                continue
            else:
                newArticle[word] = value
        # print(newArticle)
        return newArticle

    ### 生成全文本统一的词包模型，并将每篇新闻转成特定的词向量
    def calculateArticleVector(self):
        index = 0
        ### 生成全文统一的词包模型
        for article in self.articleTFIDF:
            for word, value in article.items():
                if self.wordIndex.get(word, -1) == -1:
                    self.wordIndex[word] = index
                    index = index + 1
        for article in self.articleTFIDF:
            self.calculatePerArticleVectorNew(article)

        # print(self.articleVector)
        # print(len(self.wordIndex))
        ### 生成文章词向量

    def calculatePerArticleVectorNew(self, article):
        vector = dict()
        sum = 0
        for word, value in article.items():
            index = self.wordIndex.get(word, 0)
            vector[index] = value
            sum += (value * value)
        vector[-1] = sum
        self.articleVector.append(vector)

    def calculateSimilarityMatrix(self):
        count = 0
        for article in self.articleVector:
            count += len(article)

        print(len(self.articleVector))
        print("全文本总词数", len(self.wordIndex))
        print("单新闻词数", count / len(self.articleVector))
        count = 0
        for i in range(len(self.articleVector)):
            for j in range(i, len(self.articleVector)):
                value = self.similarityNew(self.articleVector[i], self.articleVector[j])
                count = count + 1
                if value == None:
                    print(self.articleVector[i])
                    print(self.articleVector[j])
                    print('\n')
                self.similarityMatrix.append(value)
        # print(self.similarityMatrix)

    def similarityNew(self, vector1, vector2):
        sum = 0.0
        if len(vector1) < len(vector2):
            for index, value in vector1.items():
                if index == -1:
                    continue
                value2 = vector2.get(index, 0)
                sum += (value2 * value)

            if vector1.get(-1) < 0.0000001 or vector2.get(-1) < 0.000001:
                return 0
        else:
            for index, value in vector2.items():
                if index == -1:
                    continue
                value2 = vector1.get(index, 0)
                sum += (value2 * value)
            if vector1.get(-1) < 0.0000001 or vector2.get(-1) < 0.000001:
                return 0
        return math.fabs(sum / (math.sqrt(vector1.get(-1) * vector2.get(-1))))

    def writeSimilarityMatrix(self):
        sum = len(self.articleNodes)
        if os.path.exists('perresult.txt'):
            os.remove('perresult.txt')
        with open('perresult.txt','w') as f:
            for i in range(len(self.articleNodes)):
                for j in range(i, len(self.articleNodes)):
                    index = (sum+(sum-i+1))*i/2 + (j-i)
                    tempResult = self.articleIndex[i] + "-->" + self.articleIndex[j] + ":" + \
                             str(self.similarityMatrix[int(index)]) +'\n'
                    f.write(tempResult)



    def getSimilarityMatrix(self):
        return self.similarityMatrix

    def getArticleNodes(self):
        return self.articleNodes

    def getWordCount(self):
        return self.wordCountNodes

    def getWordArticleNodes(self):
        return self.wordArticleNodes

    def getArticleIndex(self):
        return self.articleIndex

    def getArticleTFIDF(self):
        return self.articleTFIDF
