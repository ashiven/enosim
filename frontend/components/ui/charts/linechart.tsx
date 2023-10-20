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

const formatDate = new Intl.DateTimeFormat("en-US", {
   month: "short",
   year: "numeric",
   day: "numeric",
})

interface Datum {
   date: string
   rx: string
   tx: string
}

interface LineChartProps {
   data: Datum[]
   fill1: string
   fill2: string
}

export const MyLineChart: React.FC<LineChartProps> = ({
   data,
   fill1,
   fill2,
}) => {
   const formatted = data.map(({ date, rx, tx }) => ({
      date: formatDate.format(new Date(date)),
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
            <Line type="monotone" dataKey="rx" fill={fill1} />
            <Line
               type="monotone"
               dataKey="tx"
               fill={fill2}
               activeDot={{ r: 8 }}
            />
         </LineChart>
      </ResponsiveContainer>
   )
}
