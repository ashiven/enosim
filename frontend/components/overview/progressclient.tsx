"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { useEffect, useState } from "react"

export default function SimulationProgressClient({ data }: any) {
   const remainingRoundsNormed = Math.round(
      ((data.total_rounds - data.remaining_rounds) / data.total_rounds) * 100
   )
   const remainingSeconds = Math.round(data.round_length - data.round_duration)
   const [countdown, setCountdown] = useState(remainingSeconds)

   useEffect(() => {
      const countdownInterval = setInterval(() => {
         if (countdown > 0) {
            setCountdown(countdown - 1)
         } else {
            clearInterval(countdownInterval)
            window.location.reload()
         }
      }, 1000)

      return () => clearInterval(countdownInterval)
   }, [countdown])

   return (
      <div className="container mx-auto mt-12 mb-8">
         <Card className="mt-8">
            <CardContent>
               <div className="mt-8">
                  <div>
                     <h4 className=" font-medium leading-none">
                        Simulation Progress
                     </h4>
                  </div>
                  <Separator className="my-4" />
                  <div className="flex h-5 items-center space-x-4 text-sm mb-4">
                     <div>Round {data.round_id}</div>
                     <Separator orientation="vertical" />
                     <div>{data.remaining_rounds} Rounds remaining</div>
                     <Separator orientation="vertical" />
                     <div>{countdown}s Until next round</div>
                  </div>
                  <Progress value={remainingRoundsNormed} />
               </div>
            </CardContent>
         </Card>
      </div>
   )
}
