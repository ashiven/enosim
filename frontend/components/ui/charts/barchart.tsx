import React from "react"
import {
   Bar,
   BarChart,
   CartesianGrid,
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
   value: string
}

interface BarChartProps {
   data: Datum[]
   fill: string
}

export const MyBarChart: React.FC<BarChartProps> = ({ data, fill }) => {
   const formatted = data.map(({ date, value }) => ({
      date: formatDate.format(new Date(date)),
      value,
   }))

   return (
      <ResponsiveContainer aspect={3.5}>
         <BarChart data={formatted}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis dataKey="value" />
            <Tooltip />
            <Bar dataKey="value" fill={fill} />
         </BarChart>
      </ResponsiveContainer>
   )
}
