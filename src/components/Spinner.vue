<template>
  <svg class="spinner" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 100 100">
    <g class="spinner-g">
      <circle class="spinner-path"
              cx="50"
              cy="50"
              r="10"
              fill="none"
              stroke-width="1"
              stroke-miterlimit="10"
              stroke="#5555ff" />
    </g>
  </svg>
</template>
<style>
  svg.spinner {
    overflow: hidden;
    position: absolute;
    z-index: 1000;
    width: 20%;
    top: 50%;
    left: 50%;
    transform: translateX(-50%) translateY(-50%);
  }

  svg.spinner .spinner-g {
    animation: spinner-rotate 2s linear infinite;
    height: 50px;
    transform-origin: center center;
    width: 50px;
  }

  svg.spinner .spinner-g .spinner-path {
    stroke-dasharray: 1, 200;
    stroke-dashoffset: 0;
    animation: spinner-dash 1.5s ease-in-out infinite;
    stroke-linecap: round;
  }

  @keyframes spinner-rotate {
    100% {
      transform: rotate3d(0, 0, 1, 360deg);
    }
  }

  @keyframes spinner-dash {
    0% {
      stroke-dasharray: 1, 200;
      stroke-dashoffset: 0;
    }

    50% {
      stroke-dasharray: 89, 200;
      stroke-dashoffset: -35px;
    }

    100% {
      stroke-dasharray: 89, 200;
      stroke-dashoffset: -124px;
    }
  }
</style>
<script>
import { defineComponent } from 'vue';

export default defineComponent({})
</script>
