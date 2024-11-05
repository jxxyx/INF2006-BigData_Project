import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class TwitterDriver {
    public static void main(String[] args) throws Exception {
        // Check input arguments
        if (args.length != 2) {
            System.err.println("Usage: DelayAnalysisDriver <input path> <output path>");
            System.exit(-1);
        }

        // Set up the configuration and job
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Airline Delay Analysis");

        // Set driver class
        job.setJarByClass(TwitterDriver.class);

        // Set mapper and reducer classes
        job.setMapperClass(TwitterMapper.class);
        job.setReducerClass(TwitterReducer.class);

        // Set output key and value types
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        // Set input and output paths
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        // Exit based on job success
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
