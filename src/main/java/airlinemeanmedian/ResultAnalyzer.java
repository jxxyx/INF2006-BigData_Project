package airlinemeanmedian;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.FileStatus;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.*;

public class ResultAnalyzer {
    public static void analyzeResults(String outputPath) throws Exception {
        Configuration conf = new Configuration();

        // Let EMR handle the filesystem configuration
        Path path = new Path(outputPath);
        FileSystem fs = FileSystem.get(path.toUri(), conf);

        Map<String, Map<String, String>> channelStats = new HashMap<>();
        String currentChannel = null;
        Map<String, String> currentStats = new HashMap<>();

        FileStatus[] fileStatuses = fs.listStatus(path);
        for (FileStatus status : fileStatuses) {
            if (status.getPath().getName().startsWith("part-r-")) {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(fs.open(status.getPath())))) {

                    String line;
                    while ((line = reader.readLine()) != null) {
                        line = line.trim();
                        if (line.contains("Channel:")) {
                            if (currentChannel != null) {
                                channelStats.put(currentChannel, new HashMap<>(currentStats));
                                currentStats.clear();
                            }
                            currentChannel = line.substring(line.indexOf(":") + 1).trim();
                        }
                        else if (line.startsWith("Mean Trust Score:")) {
                            currentStats.put("Mean", line.substring(line.indexOf(":") + 1).trim());
                        }
                        else if (line.startsWith("Median Trust Score:")) {
                            currentStats.put("Median", line.substring(line.indexOf(":") + 1).trim());
                        }
                        else if (line.startsWith("Standard Deviation:")) {
                            currentStats.put("StdDev", line.substring(line.indexOf(":") + 1).trim());
                        }
                        else if (line.startsWith("Sample Size:")) {
                            currentStats.put("SampleSize", line.substring(line.indexOf(":") + 1).trim());
                        }
                        else if (line.startsWith("Min Score:")) {
                            currentStats.put("Min", line.substring(line.indexOf(":") + 1).trim());
                        }
                        else if (line.startsWith("Max Score:")) {
                            currentStats.put("Max", line.substring(line.indexOf(":") + 1).trim());
                        }
                    }
                }

                if (currentChannel != null) {
                    channelStats.put(currentChannel, new HashMap<>(currentStats));
                }
            }
        }

        // Create CSV file in the same filesystem
        Path csvFile = new Path(outputPath + "/consolidated_results.csv");
        try (FSDataOutputStream outputStream = fs.create(csvFile)) {
            // Write CSV header
            outputStream.writeBytes("Channel,Mean Trust Score,Median Trust Score,Standard Deviation,Sample Size,Min Score,Max Score\n");

            // Write data rows
            for (Map.Entry<String, Map<String, String>> entry : channelStats.entrySet()) {
                StringBuilder line = new StringBuilder();
                Map<String, String> stats = entry.getValue();

                line.append(entry.getKey()).append(",");
                line.append(stats.getOrDefault("Mean", "")).append(",");
                line.append(stats.getOrDefault("Median", "")).append(",");
                line.append(stats.getOrDefault("StdDev", "")).append(",");
                line.append(stats.getOrDefault("SampleSize", "")).append(",");
                line.append(stats.getOrDefault("Min", "")).append(",");
                line.append(stats.getOrDefault("Max", "")).append("\n");

                outputStream.writeBytes(line.toString());
            }
        }

        System.out.println("Analysis complete. Results written to: " + csvFile);
        System.out.println("Total channels analyzed: " + channelStats.size());
    }
}