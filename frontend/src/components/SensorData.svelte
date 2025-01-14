<script lang="ts">
  import { onMount } from 'svelte';

  export let title: string;
  export let yAxisTitle: string;
  export let data: Array<{ id: number; temperature: number; humidity: number; timestamp: string }>;

  let ApexChart;
  let isClient = false;
  let chart: any;

  let chartId = `chart-${Math.random().toString(36).substring(2, 10)}`;

  const options = {
    chart: {
      type: 'line',
      background: '#111827',
      foreColor: '#9ca3af',
      animations: {
        enabled: true,
        easing: 'smooth',
        dynamicAnimation: {
          speed: 800,
        },
      },
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
      },
      fontFamily: 'Inter, system-ui, sans-serif',
    },
    title: {
      text: title,
      style: {
        fontSize: '20px',
        fontWeight: '500',
        color: '#f3f4f6'
      }
    },
    xaxis: {
      type: 'datetime',
      title: {
        text: 'Time',
        style: {
          fontSize: '14px',
          color: '#9ca3af'
        }
      },
      labels: {
        style: {
          fontSize: '12px',
          colors: '#9ca3af'
        },
        datetimeFormatter: {
          hour: 'HH:mm',
          day: 'MMM dd',
        },
        datetimeUTC: false
      },
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      }
    },
    yaxis: {
      title: {
        text: yAxisTitle,
        style: {
          fontSize: '14px',
          color: '#9ca3af'
        }
      },
      labels: {
        style: {
          fontSize: '12px',
          colors: '#9ca3af'
        }
      }
    },
    grid: {
      borderColor: '#1f2937',
      strokeDashArray: 4,
      xaxis: {
        lines: {
          show: false
        }
      },
      yaxis: {
        lines: {
          show: true,
          opacity: 0.1
        }
      }
    },
    stroke: {
      curve: 'smooth',
      width: 7,  // Made the line wider
      colors: ['#f97316']  // Orange color
    },
    colors: ['#f97316'],  // Orange color
    fill: {
      type: 'solid',
    },
    tooltip: {
      enabled: true,
      theme: 'dark',
      x: {
        format: 'MMM dd HH:mm'
      },
      style: {
        fontSize: '12px',
      },
      background: {
        enabled: true,
        foreColor: '#f3f4f6',
      }
    },
    dataLabels: {
      enabled: false,
    },
    markers: {
      size: 0,
      strokeWidth: 0,
      hover: {
        size: 0
      }
    }
  };

  let series: Array<{ name: string; data: Array<{ x: number; y: number }> }> = [
    {
      name: yAxisTitle,
      data: [],
    },
  ];

  function adjustToGMT5(timestamp: string): number {
    const date = new Date(timestamp);
    const offset = -5 * 60 * 60 * 1000;
    return date.getTime() + offset;
  }

  function updateChartData() {
    const isTemperature = yAxisTitle.toLowerCase().includes('temperature');
    const yField = isTemperature ? 'temperature' : 'humidity';

    series = [
      {
        name: yAxisTitle,
        data: data.map((d) => ({
          x: adjustToGMT5(d.timestamp),
          y: isTemperature 
            ? Number(((d[yField] * 9/5) + 32).toFixed(1))
            : Number(d[yField].toFixed(1)),
        })),
      },
    ];

    if (chart) {
      chart.updateSeries(series);
    }
  }

  $: if (data && chart) {
    updateChartData();
  }

  onMount(async () => {
    isClient = true;
    const module = await import('apexcharts');
    ApexChart = module.default;

    if (ApexChart && typeof window !== 'undefined') {
      chart = new ApexChart(document.querySelector(`#${chartId}`), {
        ...options,
        series,
      });
      chart.render();
      updateChartData();
    }
  });
</script>

{#if isClient}
  <div id="{chartId}" style="margin: 1.5rem 0; padding: 1rem; border-radius: 0.75rem; background: #111827;"></div>
{:else}
  <p class="text-gray-300">Loading chart...</p>
{/if}
