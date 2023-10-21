"use client"
import { MyAreaGraph } from "@/components/charts/areagraph"
import { MyLineChart } from "@/components/charts/linechart"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function ContainerChart({ data }: any) {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <Card className="p-5">
            <Tabs defaultValue="cpu">
               <TabsList>
                  <TabsTrigger value="cpu">CPU Usage</TabsTrigger>
                  <TabsTrigger value="ram">RAM Usage</TabsTrigger>
                  <TabsTrigger value="network">Network Usage</TabsTrigger>
               </TabsList>
               {/* CPU Usage */}
               <TabsContent value="cpu">
                  <MyAreaGraph
                     name="CPU Usage %"
                     data={data.cpuData}
                     stroke="#8884d8"
                     fill="#cfeafc"
                  />
               </TabsContent>
               {/* RAM Usage */}
               <TabsContent value="ram">
                  <MyAreaGraph
                     name="RAM Usage %"
                     data={data.ramData}
                     stroke="#00bd56"
                     fill="#ccf3f3"
                  />
               </TabsContent>
               {/* Network Usage */}
               <TabsContent value="network">
                  <MyLineChart
                     data={data.netData}
                     stroke1="#8884d8"
                     stroke2="#82ca9d"
                     name1="Received in kB"
                     name2="Transmitted in kB"
                  />
               </TabsContent>
            </Tabs>
         </Card>
      </div>
   )
}
