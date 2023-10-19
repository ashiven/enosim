import React from "react"
import {
   CartesianGrid,
   Line,
   LineChart,
   ResponsiveContainer,
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
   line1: string
   line2: string
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
   const formatted = data.map(({ date, line1, line2 }) => ({
      date: formatDate.format(new Date(date)),
      line1,
      line2,
   }))

   return (
      <ResponsiveContainer aspect={3.5}>
         <LineChart data={formatted}>
            <XAxis dataKey="date" />
            <YAxis />
            <CartesianGrid strokeDasharray="3 3" />
            <Line dataKey="line1" fill={fill1} />
            <Line dataKey="line2" fill={fill2} />
         </LineChart>
      </ResponsiveContainer>
   )
}
