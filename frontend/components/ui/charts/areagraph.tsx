import React from "react"
import {
   Area,
   AreaChart,
   CartesianGrid,
   ResponsiveContainer,
   Tooltip,
   XAxis,
   YAxis,
} from "recharts"

const formatter = new Intl.DateTimeFormat("en-US", {
   month: "short",
   year: "numeric",
   day: "numeric",
})

interface Datum {
   date: string
   value: string
}

interface AreaGraphProps {
   data: Datum[]
   stroke: string
   fill: string
}

export const MyAreaGraph: React.FC<AreaGraphProps> = ({
   data,
   stroke,
   fill,
}) => {
   const formatted = data.map(({ date, value }) => ({
      date: formatter.format(new Date(date)),
      value,
   }))

   return (
      <ResponsiveContainer aspect={3.5}>
         <AreaChart data={formatted}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis dataKey="value" />
            <Tooltip label="Daily Revenue" />
            <Area type="monotone" dataKey="value" stroke={stroke} fill={fill} />
         </AreaChart>
      </ResponsiveContainer>
   )
}
