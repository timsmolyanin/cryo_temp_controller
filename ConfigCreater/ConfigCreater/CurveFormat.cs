namespace ConfigCreater
{
    internal class CurveFormat
    {
        public string XName;
        public string YName;

        public CurveFormat() 
        {
            XName = "X";
            YName = "Y";
        }

        public CurveFormat(string xName, string yName) 
        {
            XName = xName;
            YName = yName;
        }

        public override string ToString()
        {
            return XName + " vs " + YName;
        }
    }
}
