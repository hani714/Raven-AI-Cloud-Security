import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/ui/card';
import type { VulnerabilityTrend } from '@/interfaces/dashboard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface SeverityBreakdownProps {
  trends: VulnerabilityTrend[];
}

export const SeverityBreakdown = ({ trends }: SeverityBreakdownProps) => {
  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle className="font-display">Vulnerability Summary</CardTitle>
        <CardDescription className="text-muted-foreground">
          Workspace overview · last 14 days
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.4} />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getDate()} ${date.toLocaleString('default', { month: 'short' })}`;
              }}
              tick={{ fontFamily: 'JetBrains Mono', fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis tick={{ fontFamily: 'JetBrains Mono', fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--primary) / 0.4)',
                borderRadius: '8px',
                fontFamily: 'JetBrains Mono',
                fontSize: '12px',
                boxShadow: '0 0 24px -8px hsl(var(--primary) / 0.4)',
              }}
              labelStyle={{ color: 'hsl(var(--primary))', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '10px' }}
            />
            <Legend wrapperStyle={{ fontFamily: 'JetBrains Mono', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }} />
            <Line
              type="monotone"
              dataKey="critical"
              stroke="hsl(var(--severity-critical))"
              strokeWidth={2}
              dot={{ fill: 'hsl(var(--severity-critical))', r: 3 }}
              name="Critical"
              style={{ filter: 'drop-shadow(0 0 6px hsl(var(--severity-critical)))' }}
            />
            <Line
              type="monotone"
              dataKey="high"
              stroke="hsl(var(--severity-high))"
              strokeWidth={2}
              dot={{ fill: 'hsl(var(--severity-high))', r: 3 }}
              name="High"
              style={{ filter: 'drop-shadow(0 0 6px hsl(var(--severity-high)))' }}
            />
            <Line
              type="monotone"
              dataKey="medium"
              stroke="hsl(var(--severity-medium))"
              strokeWidth={2}
              dot={{ fill: 'hsl(var(--severity-medium))', r: 3 }}
              name="Medium"
              style={{ filter: 'drop-shadow(0 0 6px hsl(var(--severity-medium)))' }}
            />
            <Line
              type="monotone"
              dataKey="low"
              stroke="hsl(var(--severity-low))"
              strokeWidth={2}
              dot={{ fill: 'hsl(var(--severity-low))', r: 3 }}
              name="Low"
              style={{ filter: 'drop-shadow(0 0 6px hsl(var(--severity-low)))' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
