import React from "react"
import {
   CartesianGrid,
   Legend,
   Line,
   LineChart,
   ResponsiveContainer,
   Tooltip,
   XAxis,
   YAxis,
} from "recharts"

function getTimestamp(date: string) {
   const timestamp = date.split(" ")[1]
   return timestamp
}

interface Datum {
   date: string
   rx: string
   tx: string
}

interface LineChartProps {
   data: Datum[]
   stroke1: string
   stroke2: string
   name1: string
   name2: string
}

export const MyLineChart: React.FC<LineChartProps> = ({
   data,
   stroke1,
   stroke2,
   name1,
   name2,
}) => {
   const formatted = data
      .slice()
      .reverse()
      .map(({ date, rx, tx }) => ({
         date: getTimestamp(date),
         rx,
         tx,
      }))

   return (
      <ResponsiveContainer aspect={3.5}>
         <LineChart data={formatted}>
            <XAxis dataKey="date" />
            <YAxis />
            <CartesianGrid strokeDasharray="3 3" />
            <Tooltip />
            <Legend />
            <Line name={name1} type="monotone" dataKey="rx" stroke={stroke1} />
            <Line
               name={name2}
               type="monotone"
               dataKey="tx"
               stroke={stroke2}
               activeDot={{ r: 8 }}
            />
         </LineChart>
      </ResponsiveContainer>
   )
}
