package jingyi;


import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.search.similarities.BooleanSimilarity;
import org.apache.lucene.search.similarities.LMDirichletSimilarity;
import org.apache.lucene.search.similarities.LMJelinekMercerSimilarity;
import org.apache.lucene.search.similarities.TFIDFSimilarity;
import org.apache.lucene.store.FSDirectory;
import jingyi.myTfidf;

public class SearcherMovies {
	public SearcherMovies(){}
	public static void main(String[] args) throws Exception{
		SearcherMovies sm = new SearcherMovies();
		String answer = sm.SearchAnswer("近期有什么好看的电影？",0);
		System.out.println(answer);//先返回一项试试
	}
	
	public  String SearchAnswer(String question,int sim) throws ParseException, IOException
	{
		String answer="";
		String index="index_";          //索引位置
		String defaultField ="content"; //查询默认为content域
		int hitsPerPage=10;             //单页数量
		IndexReader reader = DirectoryReader.open(FSDirectory.open(Paths.get(index)));
		IndexSearcher searcher = new IndexSearcher(reader);
		Analyzer analyzer = new StandardAnalyzer();
		BufferedReader in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));//输入流
		QueryParser parser = new QueryParser(defaultField, analyzer);
		
		//概率模型
		BM25Similarity bmsim = new BM25Similarity();//k1 = 1.2, b = 0.75.
		if(sim==0){
			searcher.setSimilarity(bmsim);	//设置为BM25模型评分  目前是默认的评分算法
		}
		BooleanSimilarity boolsim = new BooleanSimilarity();//布尔模型
		if(sim==1){
			searcher.setSimilarity(boolsim);
		}
		
		TFIDFSimilarity tfidfsim = (TFIDFSimilarity) new myTfidf(); //向量空间模型
		if(sim==2){
			searcher.setSimilarity(tfidfsim); //设置为TFIDF模型评分
		}
		//语言模型
		LMDirichletSimilarity Dirichletsim = new LMDirichletSimilarity();//狄里克雷语言模型  默认μ为2000（float μ）
		if(sim==3){
			searcher.setSimilarity(Dirichletsim);
		}
		
		LMJelinekMercerSimilarity JelinekMercersim = new LMJelinekMercerSimilarity((float) 0.9);//参数λ
		if(sim==4){
			searcher.setSimilarity(JelinekMercersim); 						            //线性插值
		}
		
		String line="";
		line = question.trim();
		if (line.length()==0){
			return "";
		}
		Query query =parser.parse(line);
		//System.out.println("Searching for: "+query.toString(defaultField));
		answer = doPagingSearch(in, searcher, query, hitsPerPage);//??
		reader.close();
		return answer;
	}
	/*
	*
	*/
	public static String doPagingSearch(BufferedReader in, IndexSearcher searcher,Query query,int hitsPerPage) throws IOException
	{
		TopDocs results = searcher.search(query, 5*hitsPerPage);
		ScoreDoc[] hits = results.scoreDocs;
		int numTotalHits =  results.totalHits;
		String answer="";
		//System.out.println(numTotalHits+" total maching documents");
		if(numTotalHits==0){
			return "";
		}
		int start=0;
		int end = Math.min(numTotalHits,hitsPerPage);
		while(true){
			if(end>hits.length){
				System.out.println("Only results 1 - "+hits.length+"of"+numTotalHits+"total maching documents collected");
				System.out.println("Collect more (y/n)?");
				String line = in.readLine();
				if (line.length()==0||line.charAt(0)=='n')
				{
					break;
				}
				hits = searcher.search(query, numTotalHits).scoreDocs;
			}
			end = Math.min(hits.length,start+hitsPerPage);
			for(int i=start;i<end;i++)
			{
				Document doc = searcher.doc(hits[i].doc);
				//float score = hits[i].score;
				String path = doc.get("path");
				if(path!=null)
				{
					//System.out.println((i+1)+". "+path+"\t分数："+score);
					String content = GetTextFromFile(path.toString());
					answer = content;
					return answer;
					/*
					if(title!=null){
						System.out.println("	——>"+title);
						System.out.println("    ——>"+content);
					}else{
						System.out.println((i+1)+". "+"No path for this document");
					}
					*/
				}
			}
			if(end==0){
				break;
			}
			if(numTotalHits >=end)
			{
				boolean quit = false;
				while(true){
					System.out.print("Press :");
					if(start - hitsPerPage >=0){
						System.out.print("(p)revious page,");
					}
					if(start+hitsPerPage < numTotalHits){
						System.out.print("(n)ext page,");
					}
					System.out.println("(q)uit");
					String line = in.readLine();
					if(line.length()==0||line.charAt(0)=='q'){
						quit = true;
						break;
					}
					if (line.charAt(0)=='p'){
						start = Math.max(0,start - hitsPerPage);
						break;
					}else if(line.charAt(0)=='n'){
						if(start+hitsPerPage<numTotalHits){
							start +=hitsPerPage;
						}
						break;
					}else{
						int page = Integer.parseInt(line);
						if((page-1)*hitsPerPage<numTotalHits){
							start = (page-1)*hitsPerPage;
							break;
						}else{
							System.out.println("No such page");
						}
					}
				}
				if(quit) break;
				end =Math.min(numTotalHits,start+hitsPerPage);
			}
		}
		return "";//没有的话
	}
	
	@SuppressWarnings("finally")
	public static String GetTextFromFile(String path){
		String filetext="";
		FileInputStream file=null;
		BufferedReader reader = null;
		InputStreamReader inputFileReader = null;
		String temp=null;
		try{
			file = new FileInputStream(path);
			inputFileReader = new InputStreamReader(file,"utf-8");
			reader = new BufferedReader(inputFileReader);
			while((temp=reader.readLine())!=null){
				filetext+=temp;
			}
			reader.close();
		}catch (IOException e){
			e.printStackTrace();
			return null;
		}finally{
			if(reader!=null){
				try{
					reader.close();
				}catch (IOException e){}
			}
			return filetext;
		}
		
	}
}
