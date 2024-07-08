package dk.aau.cs.dkwe.edao.jazero.entitylinker;

import com.github.jsonldjava.shaded.com.google.common.reflect.TypeToken;
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import dk.aau.cs.dkwe.edao.jazero.datalake.structures.table.DynamicTable;
import dk.aau.cs.dkwe.edao.jazero.datalake.structures.table.Table;
import dk.aau.cs.dkwe.edao.jazero.datalake.structures.table.TableDeserializer;
import dk.aau.cs.dkwe.edao.jazero.datalake.structures.table.TableSerializer;
import dk.aau.cs.dkwe.edao.jazero.datalake.system.Configuration;
import dk.aau.cs.dkwe.edao.jazero.datalake.system.Logger;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.server.ConfigurableWebServerFactory;
import org.springframework.boot.web.server.WebServerFactoryCustomizer;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.FileReader;
import java.io.IOException;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@SpringBootApplication
@RestController
public class EntityLinker implements WebServerFactoryCustomizer<ConfigurableWebServerFactory>
{
    private static Map<String, String> links;

    @Override
    public void customize(ConfigurableWebServerFactory factory)
    {
        factory.setPort(Configuration.getEntityLinkerPort());
    }

    public static void main(String[] args) throws IOException
    {
        try (FileReader reader = new FileReader("/index/entity-links.json"))
        {
            JsonParser parser = new JsonParser();
            JsonElement root = parser.parse(reader);
            Type mapType = new TypeToken<Map<String, String>>(){}.getType();
            links = new Gson().fromJson(root, mapType);
        }

        SpringApplication.run(EntityLinker.class, args);
    }

    @GetMapping("/ping")
    public ResponseEntity<String> ping()
    {
        Logger.log(Logger.Level.INFO, "PING");
        return ResponseEntity.ok().contentType(MediaType.TEXT_PLAIN).body("pong");
    }

    private static String linkInput(String input)
    {
        return links.getOrDefault(input, null);
    }

    /**
     * Entry for linking input entity to KG entity
     * @param headers Requires:
     *                Content-Type: application/json
     * @param body This is a JSON body on the following format with one entry:
     *             {
     *                 "input": "<INPUT ENTITY>"
     *             }
     * @return String of KG entity node
     */
    @PostMapping("/link")
    public ResponseEntity<String> link(@RequestHeader Map<String, String> headers, @RequestBody Map<String, String> body)
    {
        if (!body.containsKey("input"))
        {
            return ResponseEntity.badRequest().body("Missing 'input' entry in body specifying entity to be linked to the EKG");
        }

        String input = body.get("input");
        String[] split = input.split("/");
        input = split[split.length - 1];

        String linkedEntity = linkInput(input);
        return ResponseEntity.ok(linkedEntity != null ? "http://dbpedia.org/resource/" + linkedEntity : "None");
    }

    /**
     * Links all entities in a table
     * @param headers Requires:
     *                Content-Type: application/json
     * @param body Must contain JSON entry "table" as seen below:
     *             {
     *                 "table": "<SERIALIZED TABLE (use TableSerializer)>"
     *             }
     * @return Serialized table according to TableSerializer
     */
    @PostMapping("/link-table")
    public ResponseEntity<String> linkTable(@RequestHeader Map<String, String> headers, @RequestBody Map<String, String> body)
    {
        String key = "table";

        if (!body.containsKey(key))
        {
            return ResponseEntity.badRequest().body("Missing '" + key + "' entry in body specifying table of entities to be linked to the EKG");
        }

        Table<String> table = TableDeserializer.create(body.get(key)).deserialize();
        Table<String> linkedTable = new DynamicTable<>();
        int rows = table.rowCount();

        for (int row = 0; row < rows; row++)
        {
            int columns = table.getRow(row).size();
            List<String> tableRow = new ArrayList<>(columns);

            for (int column = 0; column < columns; column++)
            {
                String input = table.getRow(row).get(column);
                String linked = linkInput(input);
                tableRow.add(linked != null ? linked : "None");
            }

            linkedTable.addRow(new Table.Row<>(tableRow));
        }

        return ResponseEntity.ok(TableSerializer.create(linkedTable).serialize());
    }
}
