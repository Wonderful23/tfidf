## 将整个文本看作是一张图，这张图有全局的词视图，也有文章的视图
## 词视图主要包括单个词的总数，以及在词向量中对应的维数
## 文章视图主要是将文章转成词包模型
import math
import multiprocessing
import os
import time
from multiprocessing import Process


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

    # 第一步首先构建图的全局词视图,计算满足条件的词在单篇新闻中的词频并统计单个单词出现的篇数,以及词在全文的总数

    def calculateWords(self):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        # q = multiprocessing.Queue()
        for i in range(4):
            filepath = "test/test-%s.txt" % (str(i + 1))
            p = Process(target=self.parallelcalculateWords, args=(filepath, return_dict))
            jobs.append(p)
            p.start()
        for job in jobs:
            job.join()

        values = []
        values.append(return_dict['test/test-1.txt'])
        values.append(return_dict['test/test-2.txt'])
        values.append(return_dict['test/test-3.txt'])
        values.append(return_dict['test/test-4.txt'])
        self.mergeCalculateWords(values=values)
        print("*" * 20)

        # merge parallelcalculateresult

    def mergeCalculateWords(self, values):

        self.articleNodes = values[0][0]
        self.wordCountNodes = values[0][1]
        self.wordArticleNodes = values[0][2]
        self.articleIndex = values[0][3]

        for i in range(len(values) - 1):
            tempArticleNodes = values[i + 1][0]
            tempWordCountNodes = values[i + 1][1]
            tempWordArticleNodes = values[i + 1][2]
            tempArticleIndex = values[i + 1][3]

            self.articleNodes = self.articleNodes + tempArticleNodes
            self.articleIndex = self.articleIndex + tempArticleIndex
            for word, value in tempWordCountNodes.items():
                num = self.wordCountNodes.get(word, 0)
                self.wordCountNodes[word] = num + value

            for word, value in tempWordArticleNodes.items():
                num = self.wordArticleNodes.get(word, 0)
                self.wordArticleNodes[word] = num + value

    def parallelcalculateWords(self, filepath, return_dict):
        tempArticleNodes = []  ##
        tempWordCountNodes = dict()  ## 统计词的总数
        tempWordArticleNodes = dict()  ## 统计词的篇数
        tempValue = []
        tempArticleIndex = []
        tempValue.append(tempArticleNodes)
        tempValue.append(tempWordCountNodes)
        tempValue.append(tempWordArticleNodes)
        file = open(filepath, 'r', encoding='utf-8')
        lines = []
        line = file.readline()
        lines.append(line)
        articleName = line[0:15]
        tempArticleIndex.append(articleName)
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
                    self.articlecalculatehelper(lines, tempValue)
                    lines.clear()
                    lines.append(line)
                    articleName = tempName
                    tempArticleIndex.append(articleName)
        if len(lines) != 0:
            self.articlecalculatehelper(lines, tempValue)
            # tempArticleIndex.append(articleName)
        # print("success")
        tempValue.append(tempArticleIndex)
        return_dict[filepath] = tempValue
        file.close()
        return tempValue

    # 统计词频辅助函数
    def articlecalculatehelper(self, lines, tempValue):
        articleWords = dict()
        # print(lines)
        tempArticleNodes = tempValue[0]
        tempWordCountNodes = tempValue[1]
        tempWordArticleNodes = tempValue[2]
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
                    num = tempWordCountNodes.get(tempWords[0], 0)
                    tempWordCountNodes[tempWords[0]] = num + 1
                    # 记录单词在这篇文章出现的频率
                    num = articleWords.get(tempWords[0], 0)
                    articleWords[tempWords[0]] = num + 1
        for word, value in articleWords.items():
            num = tempWordArticleNodes.get(word, 0)
            tempWordArticleNodes[word] = num + 1
        tempArticleNodes.append(articleWords)
        tempValue[0] = tempArticleNodes
        tempValue[1] = tempWordCountNodes
        tempValue[2] = tempWordArticleNodes

    ## 计算TFIDF的值，并标准化，去除尾部数据
    def calculateTFIDF(self):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        # q = multiprocessing.Queue()
        number = len(self.articleNodes) / 4
        for i in range(4):
            p = Process(target=self.parallelCalculateTFIDF, args=(i, number, return_dict))
            jobs.append(p)
            p.start()
        for job in jobs:
            job.join()

        self.articleTFIDF = return_dict[0]
        self.articleTFIDF = self.articleTFIDF + return_dict[1] + return_dict[2] + return_dict[3]
        print(self.articleTFIDF[100])

    def parallelCalculateTFIDF(self, i, number, return_dict):
        articleSum = len(self.articleNodes)
        articlelist = []
        # print(type(self.articleNodes))
        currentArticleNodes = self.articleNodes[int(i * number):int((i + 1) * number)]
        # print(type(self.articleNodes))
        for article in currentArticleNodes:
            tempArticle = dict()
            for word, value in article.items():
                sum = self.wordCountNodes.get(word, 0)
                types = self.wordArticleNodes.get(word, 0)
                Tf_Idf = value / float(sum) * math.log1p((1 + articleSum) / types)
                tempArticle[word] = Tf_Idf
            tempArticle = self.normalize(tempArticle)
            articlelist.append(tempArticle)
        return_dict[i] = articlelist

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
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        # q = multiprocessing.Queue()
        number = len(self.articleNodes) / 4
        for i in range(4):
            p = Process(target=self.parallelCalculatePerArticleVector, args=(i, number, return_dict))
            jobs.append(p)
            p.start()
        for job in jobs:
            job.join()
        self.articleVector = return_dict[0]
        self.articleVector = self.articleVector + return_dict[1] + return_dict[2] + return_dict[3]
        # print(self.articleTFIDF)

        # print(self.articleVector)
        # print(len(self.wordIndex))
        ### 生成文章词向量

    def parallelCalculatePerArticleVector(self, i, number, return_dict):
        articleVectorlist = []
        # print(type(self.articleNodes))
        currentArticleTFIDF = self.articleTFIDF[int(i * number):int((i + 1) * number)]
        # print(type(self.articleNodes))
        for article in currentArticleTFIDF:
            vector = dict()
            sum = 0
            for word, value in article.items():
                index = self.wordIndex.get(word, 0)
                vector[index] = value
                sum += (value * value)
            vector[-1] = sum
            articleVectorlist.append(vector)
        return_dict[i] = articleVectorlist

    ## 优化之后的新方法
    def calculatePerArticleVectorNew(self, article):
        vector = dict()
        sum = 0
        for word, value in article.items():
            index = self.wordIndex.get(word, 0)
            vector[index] = value
            sum += (value * value)
        vector[-1] = sum
        self.articleVector.append(vector)


    def calculateSimilarityMatrixNew(self):
        count = 0
        for article in self.articleVector:
            count += len(article)

        print(len(self.articleVector))
        print("全文本总词数", len(self.wordIndex))
        print("单新闻词数", count / len(self.articleVector))
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        # q = multiprocessing.Queue()
        number = len(self.articleNodes) / 4
        for i in range(4):
            p = Process(target=self.parallelCalculateSimilarityMatrix, args=(i, number, return_dict))
            jobs.append(p)
            p.start()
        for job in jobs:
            job.join()
        # print(return_dict.values())
        self.similarityMatrix = return_dict[0]
        self.similarityMatrix = self.similarityMatrix + return_dict[1] + return_dict[2] + return_dict[3]
        # print(self.articleTFIDF)

    def parallelCalculateSimilarityMatrix(self, index, number, return_dict):
        similarityMatrix = []
        for i in range(int(index * number), int((index + 1) * number)):
            for j in range(i, len(self.articleVector)):
                value = self.similarityNew(self.articleVector[i], self.articleVector[j])
                similarityMatrix.append(value)
        return_dict[int(index)] = similarityMatrix


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
        # print(sum, vector2.get(-1), vector1.get(-1))
        return math.fabs(sum / (math.sqrt(vector1.get(-1) * vector2.get(-1))))

    def writeSimilarityMatrix(self):
        sum = len(self.articleNodes)
        if os.path.exists('result.txt'):
            os.remove('result.txt')
        with open('result.txt', 'w') as f:
            tempResult = ""
            count = 1
            for i in range(len(self.articleNodes)):
                for j in range(i, len(self.articleNodes)):
                    index = (sum + (sum - i + 1)) * i / 2 + (j - i)
                    tempResult += self.articleIndex[i] + "-->" + self.articleIndex[j] + ":" + \
                                  str(self.similarityMatrix[int(index)]) + '\n'
                    if count % 5000 == 0:
                        f.write(tempResult)
                        tempResult = ""
                    count = count + 1
            if len(tempResult) != 0:
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
