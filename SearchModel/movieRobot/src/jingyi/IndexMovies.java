package jingyi;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Date;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.LongPoint;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

public class IndexMovies {
	public IndexMovies(){}
	public static void main(String[] args) throws Exception
	{
		IndexMovies indexclass = new IndexMovies();
		indexclass.Create_index();
	}
	public void Create_index(){
		String indexPath="index_";         //索引位置
		String docsPath ="Data/train_";  //数据存放位置
		final Path docDir = Paths.get(docsPath);
		if(!Files.isReadable(docDir))
		{
			System.out.println("Document directory:"+docDir.toAbsolutePath()+"does not exist or not readable");
			System.exit(1);
		}
		Date start =  new Date();
		try{
			System.out.println("Indexing to directory "+indexPath+"...");
			Directory dir = FSDirectory.open(Paths.get(indexPath));
			Analyzer anlyzer = new StandardAnalyzer();
			IndexWriterConfig  iwc = new IndexWriterConfig(anlyzer);
			iwc.setOpenMode(OpenMode.CREATE); //创建索引（之前有的会覆盖）
			IndexWriter writer = new IndexWriter(dir, iwc);
			indexDocs(writer, docDir);        //建立索引
			writer.close();
			Date end = new Date();
			System.out.println((end.getTime()-start.getTime())+"total milliseconds");//建立索引的总时间
		}catch(IOException e)
		{
			System.out.println("caught a "+e.getClass()+"\n with message:"+e.getMessage());
		}
	}
	/*
	* 建立索引
	*
	*/
	static void indexDocs(final IndexWriter writer,Path path) throws IOException
	{
		if(Files.isDirectory(path))
		{
			Files.walkFileTree(path, new SimpleFileVisitor<Path>()
			{
				@Override //重写
				public FileVisitResult visitFile(Path file,BasicFileAttributes attrs) throws IOException
				{
					try
					{
						indexDoc(writer, file, attrs.lastModifiedTime().toMillis());
					}catch (IOException ignore){
						//不可读就不建立索引
					}
					return FileVisitResult.CONTINUE;
				}
			});
		}else{
			indexDoc(writer, path, Files.getLastModifiedTime(path).toMillis());
		}

	}
	/*
	*在单个文档上建立索引
	*/
	static void indexDoc(IndexWriter writer, Path file, long lastModifiedTime) throws IOException
	{
		try(InputStream stream =Files.newInputStream(file))
		{
			Document doc = new Document();
			Field pathField = new StringField("path",file.toString(), Field.Store.YES); //path 域
			doc.add(pathField);
			doc.add(new LongPoint("modified",lastModifiedTime));						//修改时间域
			Field contentField = new TextField("content",new BufferedReader(new InputStreamReader(stream,StandardCharsets.UTF_8)));
			doc.add(contentField);														//文档内容域
			String pathstring = file.toString();
			int start = pathstring.lastIndexOf('\\'); 
			int end = pathstring.lastIndexOf('.');
			String filename = pathstring.substring(start+1, end);  				     //文件名
			Field titleField = new StringField("title",filename,Field.Store.YES);   //文档文件名域
			doc.add(titleField);
			//System.out.println("Adding index "+file);
			writer.addDocument(doc);
		}
	}
}
