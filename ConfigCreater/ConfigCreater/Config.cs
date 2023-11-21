using System.Globalization;
using System.Linq;
using System.Windows.Forms;

namespace ConfigCreater
{
    internal class Config
    {
        private string _sensorModel;
        private string _serialNumber;
        private string _setPoint;

        private CurveFormat _dataFormat;
        private int _numberDataFormat;

        public Config()
        {
            CultureInfo.CurrentCulture = CultureInfo.GetCultureInfo("en-US");
        }

        public string SensorModel { get => _sensorModel; set => _sensorModel = value; }
        public string SerialNumber { get => _serialNumber; set => _serialNumber = value; }
        public string SetPoint { get => _setPoint; set => _setPoint = value; }
        public int NumberDataFormat { get => _numberDataFormat; set => _numberDataFormat = value; }
        internal CurveFormat DataFormat { get => _dataFormat; set => _dataFormat = value; }

        public void Load(string config, ref DataGridView data) 
        {
            var lines = config.Split('\n');
            SensorModel = lines[0].Replace($"{"Sensor Model:", -16}", "");
            SerialNumber = lines[1].Replace($"{"Serial Number:",-16}", "");
            NumberDataFormat = int.Parse(lines[2].Replace($"{"Data Format:",-16}", "").Split(' ')[0]);
            SetPoint = lines[3].Replace($"{"SetPoint Limit:",-16}", "").Split(' ')[0];


            for (int i = 9; i < lines.Length-1; i++)
            {
                var values = lines[i].Split(' ');
                values = values.Where(item => item != "").ToArray();
                double x = double.Parse(values[1]);
                double y = double.Parse(values[2]);
                data.Rows.Add(x, y);
            }
        }

        public string Save(DataGridView data)
        {
            string config = "";

            config += $"{"Sensor Model:", -16}{SensorModel}\n";
            config += $"{"Serial Number:", -16}{SerialNumber}\n";
            config += $"{"Data Format:",-16}{_numberDataFormat,-7}({DataFormat.XName}/{DataFormat.YName})\n";
            config += $"{"SetPoint Limit:",-16}{SetPoint,-10}({DataFormat.YName})\n";
            config += $"Temperature coefficient:  1 (Negative)\n";
            config += $"{"Number of Breakpoints:",-26}{data.RowCount}\n\n";

            config += $"No.   Units      Temperature (K)\n\n";

            int number = 1;
            foreach (DataGridViewRow row in data.Rows)
            {
                if (row.Cells[0].Value == null || row.Cells[1].Value == null)
                {
                    continue;
                }

                double cellX = double.Parse(row.Cells[0].Value.ToString().Replace(',','.'));
                double cellY = double.Parse(row.Cells[1].Value.ToString().Replace(',', '.'));

                config += $"{number, 3}   ";
                config += string.Format("{0, -14}", cellX);
                config += string.Format("{0, -10:f3}", cellY);
                config += "\n";

                number++;
            }
            return config;
        }
    }
}
