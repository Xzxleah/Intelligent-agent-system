package CovertTXT;

import org.apache.tika.Tika;
import org.apache.tika.exception.TikaException;

import java.io.*;
import java.util.ArrayList;
import java.util.StringTokenizer;

public class TikaConvert {
    public static void convertFile(String file){
        try
        {
            ArrayList<String> ar = new ArrayList<String>();
            File csvFile = new File(file);
            BufferedReader br = new BufferedReader(new FileReader(csvFile));
            String line = "";

            int lineNumber = 0;
            String slidesURI = "", worksheetURI = "", labURI = "";
            String convert_slideURI = "", convert_worksheetURI = "", convert_labURI = "";
            while ((line = br.readLine()) != null) {
                if (lineNumber != 0){
                    //System.out.println(line);
                    String[] line_arr = line.split(",");
                    //The slides URI line
                    //System.out.println(line_arr[5]);
                    slidesURI = line_arr[5].substring(8);
                    convert_slideURI = slidesURI.replace("Slides", "Slide_Plain")
                                                .replace("pdf", "txt");
                    //System.out.println(convert_slideURI);
                    useTike(slidesURI,convert_slideURI);

                    //The worksheet URI line
                    worksheetURI = line_arr[9];
                    if (worksheetURI.length() > 0 ){
                        worksheetURI = worksheetURI.substring(8);
                        convert_worksheetURI = worksheetURI.replace("Worksheet", "Worksheet_Plain")
                                .replace("pdf", "txt");
                        //System.out.println(convert_slideURI);
                        useTike(worksheetURI,convert_worksheetURI);
                    }

                    //The lab URI line
                    labURI = line_arr[13];
                    if (labURI.length() > 0 ){
                        labURI = labURI.substring(8);
                        convert_labURI = labURI.replace("Labs", "Lab_Plain")
                                .replace("pdf", "txt");
                        //System.out.println(convert_slideURI);
                        useTike(labURI,convert_labURI);
                    }
                }
                lineNumber++;
            }

        } catch (IOException e) {
            e.printStackTrace();
        } catch (TikaException tika) {
            tika.printStackTrace();
        }
    }

    public static void useTike(String fileURI, String convertFile) throws TikaException, IOException {
        File file1 = new File(fileURI);

        //通过tika获取文件内容
        Tika tika = new Tika();
        String filecontent = tika.parseToString(file1);

        try{

            //要转换到的文件
            File file =new File(convertFile);

            //文件不存在就新建
            if(!file.exists()){
                file.createNewFile();
            }

            //把二进制文件内容写入doc文件
            FileWriter fw = new FileWriter(file.getAbsoluteFile());
            BufferedWriter bw = new BufferedWriter(fw);
            bw.write(filecontent);
            bw.close();

            System.out.println(convertFile + " converted is Done.");

        }catch(IOException e){
            e.printStackTrace();
        }
    }
    public static void main(String[] args) throws IOException, TikaException {
        //convertFile("C:\\unibot\\6741_Lectures.csv");
        convertFile("C:\\unibot\\6721_Lectures.csv");
    }
}
